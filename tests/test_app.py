import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture
def reset_activity_state():
    original_state = {
        name: details["participants"][:] for name, details in app_module.activities.items()
    }

    yield

    for name, details in app_module.activities.items():
        details["participants"] = original_state[name][:]


def test_get_activities_returns_available_activities(reset_activity_state):
    # Arrange
    # no special setup required

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant(reset_activity_state):
    # Arrange
    activity_name = "Chess Club"
    email = "aaa-signup-test@mergington.edu"

    before = client.get("/activities").json()
    assert email not in before[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity_name}"

    after = client.get("/activities").json()
    assert email in after[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_registration(reset_activity_state):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email_from_activity(reset_activity_state):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    before = client.get("/activities").json()
    assert email in before[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Unregistered {email} from {activity_name}"

    after = client.get("/activities").json()
    assert email not in after[activity_name]["participants"]
