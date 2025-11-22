import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal

@pytest.fixture(scope="function")
def session():
    """Database session for tests"""
    _session = SessionLocal()
    try:
        yield _session
    finally:
        _session.close()

@pytest.fixture(scope="function")
def client():
    """Test client for API requests"""
    with TestClient(app) as c:
        yield c
