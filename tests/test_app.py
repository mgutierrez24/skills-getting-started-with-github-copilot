import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Should return all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Each activity should have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Should successfully sign up a new student for an activity"""
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
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Participant should be added to activity list"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert new_email in activities[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Should return 404 if activity doesn't exist"""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Should not allow duplicate signup"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_email_format_variations(self, client, reset_activities):
        """Should accept various valid email formats"""
        # Arrange
        valid_emails = [
            "student@mergington.edu",
            "john.doe@mergington.edu",
            "student+tag@mergington.edu"
        ]
        activity_name = "Programming Class"
        
        # Act & Assert
        for email in valid_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """A student should be able to signup for multiple activities"""
        # Arrange
        email = "multistudent@mergington.edu"
        activity_1 = "Chess Club"
        activity_2 = "Programming Class"
        
        # Act
        response_1 = client.post(
            f"/activities/{activity_1}/signup",
            params={"email": email}
        )
        response_2 = client.post(
            f"/activities/{activity_2}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        activities = activities_response.json()
        assert email in activities[activity_1]["participants"]
        assert email in activities[activity_2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Should successfully unregister a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Participant should be removed from activity list"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Should return 404 if activity doesn't exist"""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_participant_not_found(self, client, reset_activities):
        """Should return 404 if participant not in activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_then_register_again(self, client, reset_activities):
        """Should allow re-registration after unregistering"""
        # Arrange
        activity_name = "Chess Club"
        email = "testuser@mergington.edu"
        
        # Act - Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Unregister
        response_unregister = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act - Re-register
        response_register = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        
        # Assert
        assert response_unregister.status_code == 200
        assert response_register.status_code == 200
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
