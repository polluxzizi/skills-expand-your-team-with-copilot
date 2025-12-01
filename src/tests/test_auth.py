"""
Tests for the Authentication API endpoints
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAuthEndpoints:
    """Test cases for authentication API endpoints"""

    @patch('src.backend.routers.auth.teachers_collection')
    def test_login_success(self, mock_collection):
        """Test successful login with valid credentials"""
        # Arrange
        from src.backend.routers.auth import hash_password
        hashed = hash_password("testpassword")
        
        mock_collection.find_one.return_value = {
            "_id": "mrodriguez",
            "username": "mrodriguez",
            "display_name": "Ms. Rodriguez",
            "password": hashed,
            "role": "teacher"
        }

        from src.backend.routers.auth import login
        
        # Act
        result = login(username="mrodriguez", password="testpassword")
        
        # Assert
        assert result["username"] == "mrodriguez"
        assert result["display_name"] == "Ms. Rodriguez"
        assert result["role"] == "teacher"
        assert "password" not in result

    @patch('src.backend.routers.auth.teachers_collection')
    def test_login_invalid_username(self, mock_collection):
        """Test login with invalid username fails"""
        # Arrange
        mock_collection.find_one.return_value = None

        from src.backend.routers.auth import login
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            login(username="nonexistent", password="password")
        
        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in str(exc_info.value.detail)

    @patch('src.backend.routers.auth.teachers_collection')
    def test_login_invalid_password(self, mock_collection):
        """Test login with invalid password fails"""
        # Arrange
        from src.backend.routers.auth import hash_password
        
        mock_collection.find_one.return_value = {
            "_id": "mrodriguez",
            "username": "mrodriguez",
            "password": hash_password("correctpassword"),
            "display_name": "Ms. Rodriguez",
            "role": "teacher"
        }

        from src.backend.routers.auth import login
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            login(username="mrodriguez", password="wrongpassword")
        
        assert exc_info.value.status_code == 401

    @patch('src.backend.routers.auth.teachers_collection')
    def test_check_session_valid(self, mock_collection):
        """Test check-session returns teacher info for valid session"""
        # Arrange
        mock_collection.find_one.return_value = {
            "_id": "mrodriguez",
            "username": "mrodriguez",
            "display_name": "Ms. Rodriguez",
            "role": "teacher"
        }

        from src.backend.routers.auth import check_session
        
        # Act
        result = check_session(username="mrodriguez")
        
        # Assert
        assert result["username"] == "mrodriguez"
        assert result["display_name"] == "Ms. Rodriguez"
        assert result["role"] == "teacher"

    @patch('src.backend.routers.auth.teachers_collection')
    def test_check_session_invalid(self, mock_collection):
        """Test check-session fails for non-existent user"""
        # Arrange
        mock_collection.find_one.return_value = None

        from src.backend.routers.auth import check_session
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            check_session(username="nonexistent")
        
        assert exc_info.value.status_code == 404
        assert "Teacher not found" in str(exc_info.value.detail)

    def test_hash_password_consistency(self):
        """Test that hash_password produces consistent results"""
        from src.backend.routers.auth import hash_password
        
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 == hash2

    def test_hash_password_different_for_different_passwords(self):
        """Test that different passwords produce different hashes"""
        from src.backend.routers.auth import hash_password
        
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        
        assert hash1 != hash2


class TestAuthHashFunction:
    """Test cases for the password hashing function"""

    def test_hash_password_returns_hex_string(self):
        """Test that hash_password returns a hex string"""
        from src.backend.routers.auth import hash_password
        
        result = hash_password("test")
        
        # SHA-256 produces 64 character hex string
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)
