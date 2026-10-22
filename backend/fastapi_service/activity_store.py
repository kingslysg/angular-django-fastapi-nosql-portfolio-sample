"""Validated activity storage with an optional MongoDB source and JSON fallback."""
from __future__ import annotations

import json
import logging
import os
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class ActivityEvent(BaseModel):
    """The stable event shape consumed by the portfolio UI and GraphQL gateway."""

    model_config = ConfigDict(extra="ignore")

    id: int
    actor: str
    action: str
    target: str
    detail: str
    time: str
    icon: str
    tone: str

    def to_record(self) -> dict[str, Any]:
        """Serialize the stable UI fields without leaking database metadata."""
        return self.model_dump()

    def searchable_text(self) -> str:
        """Return user-facing event fields as one case-insensitive search string."""
        return " ".join((self.actor, self.action, self.target, self.detail)).casefold()


class ActivityStore:
    """Read, validate, filter, and summarize the demo's activity records."""

    def __init__(self, fixture_path: Path) -> None:
        self.fixture_path = fixture_path
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DATABASE", "northstar_demo")

    @property
    def source(self) -> str:
        """Report the configured source without opening a network connection."""
        return "mongodb" if self.mongo_uri else "json"

    def _validate(self, rows: Any) -> list[ActivityEvent]:
        if not isinstance(rows, list):
            raise ValueError("Activity data must be a JSON array")
        return [ActivityEvent.model_validate(row) for row in rows]

    def _read_fixture(self) -> list[ActivityEvent]:
        with self.fixture_path.open(encoding="utf-8") as fixture:
            return self._validate(json.load(fixture))

    def _read_mongodb(self) -> list[ActivityEvent]:
        from pymongo import MongoClient

        client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=1500)
        try:
            rows = list(
                client[self.database_name]
                .activity.find({}, {"_id": 0})
                .sort("timestamp", -1)
                .limit(1000)
            )
            return self._validate(rows)
        finally:
            client.close()

    def all_events(self) -> list[ActivityEvent]:
        """Load events, falling back to the bundled fixture on MongoDB errors."""
        if not self.mongo_uri:
            return self._read_fixture()

        try:
            return self._read_mongodb()
        except (OSError, ValueError, ValidationError, PyMongoError) as error:
            logger.warning("Could not read MongoDB activity; using JSON fixture: %s", error)
        return self._read_fixture()

    def matching_events(
        self,
        *,
        actor: str | None = None,
        tone: str | None = None,
        search: str | None = None,
    ) -> list[ActivityEvent]:
        """Return every event matching the supplied filters."""
        actor_filter = actor.casefold() if actor else None
        tone_filter = tone.casefold() if tone else None
        search_filter = search.casefold().strip() if search else None
        rows = self.all_events()
        return [
            event for event in rows
            if (actor_filter is None or actor_filter in event.actor.casefold())
            and (tone_filter is None or tone_filter == event.tone.casefold())
            and (search_filter is None or search_filter in event.searchable_text())
        ]

    def list_events(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        actor: str | None = None,
        tone: str | None = None,
        search: str | None = None,
    ) -> list[ActivityEvent]:
        """Filter events and return a stable page of matching records."""
        matches = self.matching_events(actor=actor, tone=tone, search=search)
        return matches[offset:offset + limit]

    def summarize(self) -> dict[str, Any]:
        """Aggregate event counts for the activity analytics endpoint."""
        events = self.all_events()
        return {
            "totalEvents": len(events),
            "actors": dict(sorted(Counter(event.actor for event in events).items())),
            "tones": dict(sorted(Counter(event.tone for event in events).items())),
            "latestEvent": events[0].to_record() if events else None,
        }
