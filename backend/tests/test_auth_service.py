"""Tests for auth service: JWT and password functions."""
import pytest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordHashing:
    """Password hashing and verification tests."""

    def test_hash_and_verify(self):
        """Hashed password should verify correctly."""
        plain = "my-secret-password"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True

    def test_wrong_password_fails(self):
        """Wrong password should not verify."""
        hashed = hash_password("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_is_unique(self):
        """Same password should produce different hashes (salt)."""
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2
        assert verify_password("same-password", h1)
        assert verify_password("same-password", h2)


class TestJWT:
    """JWT token creation and validation tests."""

    def test_access_token_contains_claims(self):
        """Access token should contain user_id and role."""
        token = create_access_token("user-123", "user")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "user"

    def test_refresh_token_has_type(self):
        """Refresh token should have type=refresh."""
        token = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        """Decoding garbage should return empty dict."""
        result = decode_token("not-a-valid-token")
        assert result == {}

    def test_admin_role_in_token(self):
        """Admin token should contain role=admin."""
        token = create_access_token("admin-001", "admin")
        payload = decode_token(token)
        assert payload["role"] == "admin"
