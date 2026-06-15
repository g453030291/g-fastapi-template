import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def session():
    async with AsyncSessionLocal() as s:
        yield s
        await s.rollback()
