import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal

@pytest.fixture(scope="function")
def session():
    """
    创建一个直连本地库的 session，供测试函数使用
    """
    _session = SessionLocal()
    try:
        yield _session
    finally:
        _session.close()

@pytest.fixture(scope="function")
def client():
    """
    提供一个可以直接发请求的 client
    """
    with TestClient(app) as c:
        yield c
