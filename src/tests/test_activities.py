"""
Tests for the Activities API endpoints
"""

import pytest
from unittest.mock import MagicMock, patch


class TestActivitiesEndpoints:
    """Test cases for activities API endpoints"""

    @patch('src.backend.routers.activities.activities_collection')
    def test_get_activities_returns_all_activities(self, mock_collection):
        """Test that GET /activities returns all activities"""
        # Arrange
        mock_activities = [
            {
                "_id": "Chess Club",
                "description": "Learn strategies",
                "schedule": "Mondays, 3:15 PM",
                "schedule_details": {"days": ["Monday"], "start_time": "15:15", "end_time": "16:45"},
                "max_participants": 12,
                "participants": ["test@mergington.edu"]
            }
        ]
        mock_collection.find.return_value = mock_activities

        from src.backend.routers.activities import get_activities
        
        # Act
        result = get_activities()
        
        # Assert
        assert "Chess Club" in result
        assert result["Chess Club"]["description"] == "Learn strategies"

    @patch('src.backend.routers.activities.activities_collection')
    def test_get_activities_with_day_filter(self, mock_collection):
        """Test that GET /activities with day filter returns filtered activities"""
        # Arrange
        mock_activities = [
            {
                "_id": "Chess Club",
                "description": "Learn strategies",
                "schedule_details": {"days": ["Monday"], "start_time": "15:15", "end_time": "16:45"},
                "max_participants": 12,
                "participants": []
            }
        ]
        mock_collection.find.return_value = mock_activities

        from src.backend.routers.activities import get_activities
        
        # Act
        result = get_activities(day="Monday")
        
        # Assert
        mock_collection.find.assert_called_once()
        call_args = mock_collection.find.call_args[0][0]
        assert "schedule_details.days" in call_args

    @patch('src.backend.routers.activities.activities_collection')
    def test_get_available_days(self, mock_collection):
        """Test that GET /activities/days returns available days"""
        # Arrange
        mock_collection.aggregate.return_value = [
            {"_id": "Monday"},
            {"_id": "Tuesday"},
            {"_id": "Wednesday"}
        ]

        from src.backend.routers.activities import get_available_days
        
        # Act
        result = get_available_days()
        
        # Assert
        assert result == ["Monday", "Tuesday", "Wednesday"]
        mock_collection.aggregate.assert_called_once()

    @patch('src.backend.routers.activities.teachers_collection')
    @patch('src.backend.routers.activities.activities_collection')
    def test_signup_for_activity_success(self, mock_activities, mock_teachers):
        """Test successful signup for an activity"""
        # Arrange
        mock_teachers.find_one.return_value = {"_id": "mrodriguez", "username": "mrodriguez"}
        mock_activities.find_one.return_value = {
            "_id": "Chess Club",
            "participants": ["existing@mergington.edu"],
            "max_participants": 12
        }
        mock_activities.update_one.return_value = MagicMock(modified_count=1)

        from src.backend.routers.activities import signup_for_activity
        
        # Act
        result = signup_for_activity(
            activity_name="Chess Club",
            email="new@mergington.edu",
            teacher_username="mrodriguez"
        )
        
        # Assert
        assert "Signed up" in result["message"]
        assert "new@mergington.edu" in result["message"]

    @patch('src.backend.routers.activities.teachers_collection')
    @patch('src.backend.routers.activities.activities_collection')
    def test_signup_without_teacher_auth_fails(self, mock_activities, mock_teachers):
        """Test that signup without teacher authentication fails"""
        from src.backend.routers.activities import signup_for_activity
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(
                activity_name="Chess Club",
                email="test@mergington.edu",
                teacher_username=None
            )
        
        assert exc_info.value.status_code == 401

    @patch('src.backend.routers.activities.teachers_collection')
    @patch('src.backend.routers.activities.activities_collection')
    def test_signup_already_registered_fails(self, mock_activities, mock_teachers):
        """Test that signing up twice fails"""
        # Arrange
        mock_teachers.find_one.return_value = {"_id": "mrodriguez"}
        mock_activities.find_one.return_value = {
            "_id": "Chess Club",
            "participants": ["existing@mergington.edu"],
            "max_participants": 12
        }

        from src.backend.routers.activities import signup_for_activity
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(
                activity_name="Chess Club",
                email="existing@mergington.edu",
                teacher_username="mrodriguez"
            )
        
        assert exc_info.value.status_code == 400
        assert "Already signed up" in str(exc_info.value.detail)

    @patch('src.backend.routers.activities.teachers_collection')
    @patch('src.backend.routers.activities.activities_collection')
    def test_unregister_from_activity_success(self, mock_activities, mock_teachers):
        """Test successful unregistration from an activity"""
        # Arrange
        mock_teachers.find_one.return_value = {"_id": "mrodriguez"}
        mock_activities.find_one.return_value = {
            "_id": "Chess Club",
            "participants": ["existing@mergington.edu"],
            "max_participants": 12
        }
        mock_activities.update_one.return_value = MagicMock(modified_count=1)

        from src.backend.routers.activities import unregister_from_activity
        
        # Act
        result = unregister_from_activity(
            activity_name="Chess Club",
            email="existing@mergington.edu",
            teacher_username="mrodriguez"
        )
        
        # Assert
        assert "Unregistered" in result["message"]

    @patch('src.backend.routers.activities.teachers_collection')
    @patch('src.backend.routers.activities.activities_collection')
    def test_unregister_not_registered_fails(self, mock_activities, mock_teachers):
        """Test that unregistering when not registered fails"""
        # Arrange
        mock_teachers.find_one.return_value = {"_id": "mrodriguez"}
        mock_activities.find_one.return_value = {
            "_id": "Chess Club",
            "participants": ["other@mergington.edu"],
            "max_participants": 12
        }

        from src.backend.routers.activities import unregister_from_activity
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity(
                activity_name="Chess Club",
                email="notregistered@mergington.edu",
                teacher_username="mrodriguez"
            )
        
        assert exc_info.value.status_code == 400
        assert "Not registered" in str(exc_info.value.detail)

    @patch('src.backend.routers.activities.teachers_collection')
    @patch('src.backend.routers.activities.activities_collection')
    def test_signup_activity_not_found(self, mock_activities, mock_teachers):
        """Test signup for non-existent activity fails"""
        # Arrange
        mock_teachers.find_one.return_value = {"_id": "mrodriguez"}
        mock_activities.find_one.return_value = None

        from src.backend.routers.activities import signup_for_activity
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(
                activity_name="NonExistent",
                email="test@mergington.edu",
                teacher_username="mrodriguez"
            )
        
        assert exc_info.value.status_code == 404
