import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from GraphCap.config.router import router


@pytest.fixture
def app():
    """Create a test FastAPI application with our router mounted"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client using the test app"""
    return TestClient(app)
