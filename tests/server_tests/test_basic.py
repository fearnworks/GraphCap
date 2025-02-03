"""
# SPDX-License-Identifier: Apache-2.0
graphcap.tests.server_tests.test_basic

Basic server integration tests.

Key features:
- Server health check endpoint testing
- Basic API response validation
- HTTP status code verification
- Response format validation

Classes:
    None (contains test functions only)
"""

import pytest
from httpx import AsyncClient


@pytest.fixture
def client():
    """Create a test client using the test app"""
    return AsyncClient(base_url="http://localhost:32100")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.server
async def test_health_check(client: AsyncClient):
    """
    GIVEN a running server
    WHEN the health check endpoint is called
    THEN should return a 200 status code
    AND should return a JSON object with a status of "healthy"
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
