def test_health_check(client):
    """
    GIVEN a running server
    WHEN the health check endpoint is called
    THEN should return a 200 status code
    AND should return a JSON object with a status of "healthy"
    """
    response = client.get("/server/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
