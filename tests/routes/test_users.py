from unittest import mock
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status

from src.services.auth import get_current_user


user_data_admin = {
    "id": 1,
    "username": "dad",
    "email": "dad@gmail.com",
    "password": "12345678",
    "role": "admin",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

user_data_not_admin = {
    "id": 1,
    "username": "dad",
    "email": "dad@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}


@pytest.mark.asyncio
async def test_me(client, auth_headers):
    async def override_get_current_user():
        return user_data_admin

    from main import app  

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.get("/api/users/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == user_data_admin["email"]
    assert response.json()["username"] == user_data_admin["username"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_me_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.get("/api/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
