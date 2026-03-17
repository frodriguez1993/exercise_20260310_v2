"""
Tests for the Mergington High School API
Uses the AAA (Arrange-Act-Assert) pattern for clear test structure
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the original activities state for test isolation
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before and after each test"""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


class TestRootRedirect:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """GET / should redirect to /static/index.html"""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for retrieving activities"""

    def test_get_activities_returns_all_activities(self, client):
        """GET /activities should return all activities"""
        # Arrange
        # (activities fixture handles setup)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9  # Total number of activities


class TestSignupForActivity:
    """Tests for signing up for an activity"""

    def test_signup_new_participant_succeeds(self, client):
        """POST /activities/{activity_name}/signup should add new participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_already_registered_returns_400(self, client):
        """POST /activities/{activity_name}/signup should return 400 for duplicate signup"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """POST /activities/{activity_name}/signup should return 404 for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Tests for removing participants from activities"""

    def test_remove_existing_participant_succeeds(self, client):
        """DELETE /activities/{activity_name}/participants should remove participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_nonexistent_participant_returns_404(self, client):
        """DELETE /activities/{activity_name}/participants should return 404 for nonexistent participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # Not signed up

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """DELETE /activities/{activity_name}/participants should return 404 for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
