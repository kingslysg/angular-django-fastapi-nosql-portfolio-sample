"""HTTP contract tests for the analytics endpoints."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main
from activity_store import ActivityStore


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    fixture = tmp_path / "activity.json"
    fixture.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "actor": "Ava Chen",
                    "action": "deployed",
                    "target": "Analytics API",
                    "detail": "Python service is live",
                    "time": "2026-10-21T10:00:00Z",
                    "icon": "rocket",
                    "tone": "success",
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
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(main, "activity_store", ActivityStore(fixture))
    with TestClient(main.app) as test_client:
        yield test_client


def test_health_reports_service_and_activity_source(client: TestClient) -> None:
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "fastapi-analytics",
        "status": "ok",
        "activitySource": "json",
    }


def test_activity_endpoint_filters_and_paginates(client: TestClient) -> None:
    response = client.get(
        "/api/analytics/activity",
        params={"actor": "ava", "search": "PYTHON", "limit": 1},
    )

    assert response.status_code == 200
    assert [event["id"] for event in response.json()] == [1]


def test_activity_endpoint_rejects_out_of_range_limit(client: TestClient) -> None:
    response = client.get("/api/analytics/activity", params={"limit": 101})

    assert response.status_code == 422


def test_activity_summary_endpoint_returns_aggregate(client: TestClient) -> None:
    response = client.get("/api/analytics/activity/summary")

    assert response.status_code == 200
    assert response.json()["totalEvents"] == 2
    assert response.json()["latestEvent"]["id"] == 1


def test_activity_export_returns_filtered_csv(client: TestClient) -> None:
    response = client.get("/api/analytics/activity/export", params={"tone": "success"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'attachment; filename="portfolio-activity.csv"' in response.headers[
        "content-disposition"
    ]
    assert response.text.splitlines() == [
        "id,actor,action,target,detail,time,icon,tone",
        "1,Ava Chen,deployed,Analytics API,Python service is live,2026-10-21T10:00:00Z,rocket,success",
    ]
