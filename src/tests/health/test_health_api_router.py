from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

class TestHealthApiRouter:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}