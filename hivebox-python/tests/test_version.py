from fastapi.testclient import TestClient


def test_version_endpoint_returns_200_and_correct_structure():
    """Test that GET /version returns 200 status and correct JSON structure"""
    from main import app
    from app.config import settings

    client = TestClient(app)
    response = client.get("/version")

    assert response.status_code == 200
    assert "version" in response.json()
    assert isinstance(response.json()["version"], str)
    assert response.json()["version"] == settings.app_version
