import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Save the original activities state for test isolation
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset activities before each test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield

client = TestClient(app)

def test_get_activities():
    # Arrange: (handled by fixture)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    assert email not in activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity}"

def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity}"

def test_unregister_not_registered():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"

def test_unregister_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
