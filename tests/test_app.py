from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_unregister_participant():
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")
    assert response.status_code == 200
    payload = response.json()
    assert "Unregistered" in payload["message"]

    activities = client.get("/activities").json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
