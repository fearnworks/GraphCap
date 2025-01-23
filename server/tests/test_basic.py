def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/server/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
