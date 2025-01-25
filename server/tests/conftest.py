import json
import os
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from GraphCap.config.router import router

# Load environment variables from .env
load_dotenv()


def log_test_response(test_name: str, response: dict, log_file: str = "test_logs.jsonl"):
    """Log test responses to a JSON Lines file"""
    log_entry = {"timestamp": datetime.now().isoformat(), "test_name": test_name, "response": response}

    # Ensure the directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "a") as f:
        json.dump(log_entry, f)
        f.write("\n")


@pytest.fixture(scope="session")
def test_logger():
    """Fixture to provide the logging function to tests"""
    return log_test_response


# Clean up log file at the start of test session
@pytest.fixture(scope="session", autouse=True)
def clean_logs():
    """Clean up log file at the start of test session"""
    if os.path.exists("test_logs.jsonl"):
        os.remove("test_logs.jsonl")


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
