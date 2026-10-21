"""Analytics demo API. Uses MongoDB when configured, otherwise local JSON fixtures."""
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Northstar Analytics API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET'],
    allow_headers=['*'],
)
FIXTURE = Path(__file__).resolve().parents[2] / 'data' / 'activity.json'


def get_events() -> list[dict[str, Any]]:
    uri = os.getenv('MONGODB_URI')
    if uri:
        from pymongo import MongoClient
        client = MongoClient(uri, serverSelectionTimeoutMS=1500)
        database = client[os.getenv('MONGODB_DATABASE', 'northstar_demo')]
        events = list(database.activity.find({}, {'_id': 0}).sort('timestamp', -1).limit(20))
        client.close()
        return events
    with FIXTURE.open(encoding='utf-8') as fixture:
        return json.load(fixture)


@app.get('/health/')
def health():
    return {'service': 'fastapi-analytics', 'status': 'ok'}


@app.get('/api/analytics/summary')
def summary():
    return {'activeProjects': 4, 'shipped': 8, 'apiRequests': '24.8', 'availability': '99.9'}


@app.get('/api/analytics/activity')
def activity():
    return get_events()
