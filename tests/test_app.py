"""
Test suite for Mergington High School Activities API
Tests use the AAA (Arrange-Act-Assert) pattern
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Call GET /activities
        Act: Fetch all activities
        Assert: Verify all 9 activities are returned
        """
        # Arrange (implicit via fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Tennis Club" in activities
        assert "Art Studio" in activities
        assert "Music Ensemble" in activities
        assert "Robotics Club" in activities
        assert "Science Club" in activities

    def test_get_activities_includes_required_fields(self, client):
        """
        Arrange: Call GET /activities
        Act: Fetch activities data
        Assert: Verify each activity has required fields
        """
        # Arrange (implicit via fixture)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_initial_participants(self, client):
        """
        Arrange: Call GET /activities
        Act: Fetch activities data
        Assert: Verify participants list is populated correctly
        """
        # Arrange (implicit via fixture)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Call GET /
        Act: Request root path
        Assert: Verify redirect to /static/index.html
        """
        # Arrange (implicit via fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupHappyPath:
    """Tests for successful POST /activities/{activity_name}/signup scenarios"""

    def test_signup_successful(self, client):
        """
        Arrange: Prepare new student email
        Act: Sign up for an activity
        Assert: Verify success response and email added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_email_added_to_participants(self, client):
        """
        Arrange: Prepare new student email
        Act: Sign up for activity, then fetch activities
        Assert: Verify email appears in participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "testuser@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_different_emails(self, client):
        """
        Arrange: Prepare multiple unique student emails
        Act: Sign up all for same activity
        Assert: Verify all emails in participants list
        """
        # Arrange
        activity_name = "Basketball Team"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act
        for email in emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestSignupErrorCases:
    """Tests for error scenarios in POST /activities/{activity_name}/signup"""

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare request for non-existent activity
        Act: Attempt signup for invalid activity
        Assert: Verify 404 status code and error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Arrange: Student already signed up for activity
        Act: Attempt to sign up same student again
        Assert: Verify 400 status code and error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_without_email_parameter_returns_422(self, client):
        """
        Arrange: Prepare request without email parameter
        Act: Send signup request missing required email
        Assert: Verify 422 validation error
        """
        # Arrange
        activity_name = "Tennis Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422


class TestSignupEdgeCases:
    """Tests for edge cases in POST /activities/{activity_name}/signup"""

    def test_signup_empty_email_string(self, client):
        """
        Arrange: Prepare signup with empty email
        Act: Sign up with empty email string
        Assert: Verify email is accepted and added (no format validation)
        """
        # Arrange
        activity_name = "Art Studio"
        email = ""
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_name_case_sensitivity(self, client):
        """
        Arrange: Prepare signup with different case activity name
        Act: Sign up using lowercase activity name
        Assert: Verify case sensitivity (lowercase should fail with 404)
        """
        # Arrange
        activity_name_correct = "Chess Club"
        activity_name_wrong_case = "chess club"
        email = "student@mergington.edu"
        
        # Act - Correct case
        response_correct = client.post(
            f"/activities/{activity_name_correct}/signup",
            params={"email": email}
        )
        
        # Act - Wrong case (should fail)
        response_wrong = client.post(
            f"/activities/{activity_name_wrong_case}/signup",
            params={"email": "another@mergington.edu"}
        )
        
        # Assert
        assert response_correct.status_code == 200
        assert response_wrong.status_code == 404

    def test_signup_special_characters_in_email(self, client):
        """
        Arrange: Prepare email with special characters
        Act: Sign up with special character email
        Assert: Verify email is accepted (no format validation)
        """
        # Arrange
        activity_name = "Music Ensemble"
        email = "user+tag@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200

    def test_signup_with_whitespace_in_email(self, client):
        """
        Arrange: Prepare email with leading/trailing whitespace
        Act: Sign up with whitespace-padded email
        Assert: Verify whitespace is preserved (no trimming)
        """
        # Arrange
        activity_name = "Robotics Club"
        email_with_space = " student@mergington.edu "
        email_clean = "clean@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_with_space}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_clean}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert - Both should be added as different emails
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email_with_space in activities[activity_name]["participants"]
        assert email_clean in activities[activity_name]["participants"]

    def test_signup_url_encoded_activity_name(self, client):
        """
        Arrange: Activity name with spaces (URL encoded)
        Act: Sign up for activity with spaces in name
        Assert: Verify signup works with URL-encoded names
        """
        # Arrange
        activity_name = "Programming Class"
        email = "coder@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
