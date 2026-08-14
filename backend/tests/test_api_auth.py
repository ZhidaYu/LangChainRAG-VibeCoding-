"""Tests for Auth API endpoints."""
import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health endpoint should return 200."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
async def test_register_user(client):
    """Register should create user and return tokens."""
    response = await client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "test123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    """Registering same username should fail."""
    await client.post(
        "/api/auth/register",
        json={"username": "dupuser", "password": "test123456"},
    )
    response = await client.post(
        "/api/auth/register",
        json={"username": "dupuser", "password": "another123456"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    """Admin login should succeed."""
    response = await client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Wrong password should fail."""
    response = await client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint(client):
    """GET /me should return current user."""
    # Login first
    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "123456"},
    )
    token = login_resp.json()["access_token"]

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_me_without_token(client):
    """GET /me without token should fail."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_kb_endpoint_requires_admin(client):
    """KB stats should require authentication."""
    response = await client.get("/api/kb/stats")
    assert response.status_code == 401
