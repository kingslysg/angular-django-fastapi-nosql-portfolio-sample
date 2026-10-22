"""Tests for activity fixture loading, filtering, fallback, and summaries."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from pymongo.errors import ServerSelectionTimeoutError

from activity_store import ActivityStore


@pytest.fixture
def fixture_path(tmp_path: Path) -> Path:
    rows = [
        {
            "id": 1,
            "actor": "Ava Chen",
            "action": "deployed",
            "target": "Analytics API",
            "detail": "Python service is live",
            "time": "2026-10-21T10:00:00Z",
            "icon": "rocket",
            "tone": "success",
            "_id": "database-metadata",
        },
        {
            "id": 2,
            "actor": "Noah Patel",
            "action": "reviewed",
            "target": "Portfolio UI",
            "detail": "TypeScript changes are ready",
            "time": "2026-10-20T10:00:00Z",
            "icon": "check",
            "tone": "info",
        },
        {
            "id": 3,
            "actor": "Ava Chen",
            "action": "fixed",
            "target": "CSV export",
            "detail": "Resolved a warning",
            "time": "2026-10-19T10:00:00Z",
            "icon": "wrench",
            "tone": "warning",
        },
    ]
    path = tmp_path / "activity.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def test_loads_fixture_and_omits_database_metadata(fixture_path: Path) -> None:
    store = ActivityStore(fixture_path)

    events = store.all_events()

    assert len(events) == 3
    assert events[0].actor == "Ava Chen"
    assert "_id" not in events[0].to_record()


def test_rejects_invalid_event_shape(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps([{"id": "not-an-integer"}]), encoding="utf-8")

    with pytest.raises(ValidationError):
        ActivityStore(path).all_events()


def test_rejects_non_array_fixture(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps({"event": "not a list"}), encoding="utf-8")

    with pytest.raises(ValueError, match="JSON array"):
        ActivityStore(path).all_events()


def test_filters_are_case_insensitive_and_search_event_details(fixture_path: Path) -> None:
    store = ActivityStore(fixture_path)

    results = store.matching_events(actor="AVA", tone="SUCCESS", search="PYTHON")

    assert [event.id for event in results] == [1]


def test_list_events_applies_offset_after_filtering(fixture_path: Path) -> None:
    store = ActivityStore(fixture_path)

    results = store.list_events(actor="ava", limit=1, offset=1)

    assert [event.id for event in results] == [3]


def test_summary_counts_actors_and_tones_and_reports_latest(fixture_path: Path) -> None:
    summary = ActivityStore(fixture_path).summarize()

    assert summary["totalEvents"] == 3
    assert summary["actors"] == {"Ava Chen": 2, "Noah Patel": 1}
    assert summary["tones"] == {"info": 1, "success": 1, "warning": 1}
    assert summary["latestEvent"]["id"] == 1


def test_uses_fixture_when_mongodb_is_unavailable(
    fixture_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MONGODB_URI", "mongodb://unavailable.invalid")
    store = ActivityStore(fixture_path)
    monkeypatch.setattr(
        store,
        "_read_mongodb",
        lambda: (_ for _ in ()).throw(ServerSelectionTimeoutError("offline")),
    )

    assert store.source == "mongodb"
    assert [event.id for event in store.all_events()] == [1, 2, 3]
