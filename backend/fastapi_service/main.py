"""Analytics demo API. Uses MongoDB when configured, otherwise local JSON fixtures."""
import csv
from io import StringIO
from pathlib import Path

from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware

from activity_store import ActivityStore

app = FastAPI(title='Northstar Analytics API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET'],
    allow_headers=['*'],
)
FIXTURE = Path(__file__).resolve().parents[2] / 'data' / 'activity.json'
activity_store = ActivityStore(FIXTURE)


@app.get('/health/')
def health():
    return {'service': 'fastapi-analytics', 'status': 'ok', 'activitySource': activity_store.source}


@app.get('/api/analytics/summary')
def summary():
    return {'activeProjects': 4, 'shipped': 8, 'apiRequests': '24.8', 'availability': '99.9'}


@app.get('/api/analytics/activity')
def activity(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    actor: str | None = Query(default=None, min_length=1, max_length=80),
    tone: str | None = Query(default=None, min_length=1, max_length=24),
    search: str | None = Query(default=None, min_length=1, max_length=160),
):
    return [event.to_record() for event in activity_store.list_events(
        limit=limit, offset=offset, actor=actor, tone=tone, search=search
    )]


@app.get('/api/analytics/activity/summary')
def activity_summary():
    return activity_store.summarize()


@app.get('/api/analytics/activity/export')
def export_activity(
    actor: str | None = Query(default=None, min_length=1, max_length=80),
    tone: str | None = Query(default=None, min_length=1, max_length=24),
    search: str | None = Query(default=None, min_length=1, max_length=160),
):
    output = StringIO(newline='')
    fields = ('id', 'actor', 'action', 'target', 'detail', 'time', 'icon', 'tone')
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for event in activity_store.matching_events(actor=actor, tone=tone, search=search):
        writer.writerow(event.to_record())
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="portfolio-activity.csv"'},
    )
