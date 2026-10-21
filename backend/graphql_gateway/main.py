"""Strawberry GraphQL gateway for the Northstar portfolio demo."""
import json
import os
from pathlib import Path
from typing import Optional

import httpx
import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'data' / 'activity.json'
DJANGO_URL = os.getenv('DJANGO_API_URL', 'http://localhost:8000')
ANALYTICS_URL = os.getenv('ANALYTICS_API_URL', 'http://localhost:8001')

@strawberry.type
class Project:
    id: str
    name: str
    type: str
    group: str
    category: str
    status: str
    status_key: str
    updated: str
    description: str
    tech: list[str]
    theme: str
    symbol: str
    cover_label: str

@strawberry.type
class Summary:
    active_projects: int
    shipped: int
    api_requests: str
    availability: str

@strawberry.type
class Activity:
    id: int
    actor: str
    action: str
    target: str
    detail: str
    time: str
    icon: str
    tone: str

async def load_projects() -> list[Project]:
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get(f'{DJANGO_URL}/api/projects/')
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        data = []
    return [Project(
        id=item['id'], name=item['name'], type=item['type'], group=item.get('group', item['type']),
        category=item['category'], status=item['status'], status_key=item.get('statusKey', 'progress'),
        updated=item['updated'], description=item['description'], tech=item['tech'], theme=item['theme'],
        symbol=item['symbol'], cover_label=item['coverLabel'],
    ) for item in data]

async def load_summary() -> Summary:
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get(f'{ANALYTICS_URL}/api/analytics/summary')
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        data = {'activeProjects': 1, 'shipped': 1, 'apiRequests': '24.8', 'availability': '99.9'}
    return Summary(data['activeProjects'], data['shipped'], str(data['apiRequests']), str(data['availability']))

async def load_activity() -> list[Activity]:
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get(f'{ANALYTICS_URL}/api/analytics/activity')
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        with FIXTURE.open(encoding='utf-8') as fixture:
            data = json.load(fixture)
    return [Activity(**item) for item in data]

@strawberry.type
class Query:
    @strawberry.field
    async def projects(self) -> list[Project]:
        return await load_projects()

    @strawberry.field
    async def summary(self) -> Summary:
        return await load_summary()

    @strawberry.field
    async def activity(self) -> list[Activity]:
        return await load_activity()

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app = FastAPI(title='Northstar Strawberry GraphQL Gateway', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)
app.include_router(graphql_app, prefix='/graphql')

@app.get('/health/')
def health():
    return {'service': 'strawberry-graphql-gateway', 'status': 'ok'}
