from unittest.mock import Mock, AsyncMock
import pytest
from sqlalchemy import select
from src.entity.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "dad",
    "email": "dad@gmail.com",
    "password": "12345678",
    "role": "user",
}

user_data_unique_email = {
    "username": "dad",
    "email": "dady@gmail.com",
    "password": "12345678",
    "role": "user",
}

user_data_unique = {
    "username": "dady",
    "email": "dady@gmail.com",
    "password": "12345678",
    "role": "user",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data
    assert data["role"] == user_data["role"]


def test_signup_same_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    assert (
        response.json()["detail"] == "A user with this email already exists."
    )


def test_signup_same_username(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data_unique_email)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "A user with this name already exists."


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "A user with this email already exists."


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not verified."


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Wrong email or password"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Wrong email or password"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_confirm_email(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    monkeypatch.setattr("src.routes.auth.get_email_from_token", mock_get_email_from_token)

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=False))
    mock_user_service.confirmed_email = AsyncMock(return_value=True)
    monkeypatch.setattr("src.routes.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirmed_email/token")
    assert response.status_code == 200
    assert response.json()["message"] == "Email has been verified."

    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.confirmed_email.assert_called_once_with("test_user@gmail.com")


@pytest.mark.asyncio
async def test_confirm_email_already_confirmed(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    monkeypatch.setattr("src.routes.auth.get_email_from_token", mock_get_email_from_token)

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=True))
    monkeypatch.setattr("src.routes.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirmed_email/token")

    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already verified."

    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.confirmed_email.assert_not_called()


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.routes.auth.send_confirm_email", mock_send_email)

    client.post("api/auth/register", json=user_data_unique)
    response = client.post(
        "api/auth/request_email", json={"email": user_data_unique["email"]}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Check your email for confirmation."


@pytest.mark.asyncio
async def test_request_email_already_confirmed(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.routes.auth.send_confirm_email", mock_send_email)

    response = client.post("api/auth/request_email", json={"email": user_data["email"]})

    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already confirmed"


@pytest.mark.asyncio
async def test_confirm_reset_password(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.routes.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.routes.auth.get_password_from_token", mock_get_password_from_token
    )

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(
        return_value=Mock(id=1, email="test_user@gmail.com")
    )
    mock_user_service.reset_password = AsyncMock(return_value=None)
    monkeypatch.setattr("src.routes.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 200
    assert response.json()["message"] == "Password successfully changed."

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.reset_password.assert_called_once_with(1, "new_hashed_password")


@pytest.mark.asyncio
async def test_confirm_reset_password_invalid_token(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value=None)
    mock_get_password_from_token = AsyncMock(return_value=None)
    monkeypatch.setattr("src.routes.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.routes.auth.get_password_from_token", mock_get_password_from_token
    )

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token."

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")


@pytest.mark.asyncio
async def test_confirm_reset_password_user_not_found(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.routes.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.routes.auth.get_password_from_token", mock_get_password_from_token
    )

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=None)
    monkeypatch.setattr("src.routes.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "User with this email address not found"
    )

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
