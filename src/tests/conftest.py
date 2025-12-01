"""
Pytest configuration and shared fixtures for Mergington High School API tests
"""

import sys
import os

# Add the src directory to the Python path for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_activities():
    """Sample activities data for testing"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
            "schedule_details": {
                "days": ["Monday", "Friday"],
                "start_time": "15:15",
                "end_time": "16:45"
            },
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
            "schedule_details": {
                "days": ["Tuesday", "Thursday"],
                "start_time": "07:00",
                "end_time": "08:00"
            },
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    }


@pytest.fixture
def sample_teacher():
    """Sample teacher data for testing"""
    return {
        "_id": "mrodriguez",
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": "hashed_password",
        "role": "teacher"
    }

