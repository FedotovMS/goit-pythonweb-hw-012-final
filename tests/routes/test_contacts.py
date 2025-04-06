import pytest
from unittest.mock import AsyncMock

from src.schemas.contacts import ContactModel
from main import app
from src.services.auth import get_current_user

user_data = {
    "id": 101,
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepassword",
    "role": "user",
    "confirmed": True,
}

contacts = [
    {
        "id": 1,
        "name": "Charlie",
        "surname": "Smith",
        "birthday": "1990-03-15",
        "email": "charlie.smith@example.com",
        "phone": "123-456-7890",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "info": "Friend from college.",
    },
    {
        "id": 2,
        "name": "Dana",
        "surname": "Brown",
        "birthday": "1992-07-22",
        "email": "dana.brown@example.com",
        "phone": "987-654-3210",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "info": None,
    },
]

payload = {
    "name": "Charlie",
    "surname": "Smith",
    "birthday": "1990-03-15",
    "email": "charlie.smith@example.com",
    "phone": "123-456-7890",
}

@pytest.fixture(autouse=True)
def override_get_current_user():
    async def mock_get_current_user():
        return user_data
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def headers():
    return {"Authorization": "Bearer testtoken"}

@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, monkeypatch, headers):
    mock_get_upcoming_birthdays = AsyncMock(return_value=contacts)
    monkeypatch.setattr("src.conf.contacts.ContactService.get_upcoming_birthdays", mock_get_upcoming_birthdays)

    response = client.get("/api/contacts/birthdays?days=7", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == len(contacts)

@pytest.mark.asyncio
async def test_get_contacts_no_filters(client, monkeypatch, headers):
    mock_get_contacts = AsyncMock(return_value=contacts)
    monkeypatch.setattr("src.conf.contacts.ContactService.get_contacts", mock_get_contacts)

    response = client.get("/api/contacts/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == len(contacts)
    assert response.json()[0]["email"] == contacts[0]["email"]
    mock_get_contacts.assert_called_once_with("", "", "", 0, 100, user_data)

@pytest.mark.asyncio
async def test_get_contacts_with_filters(client, monkeypatch, headers):
    filtered_contacts = [contacts[0]]
    mock_get_contacts = AsyncMock(return_value=filtered_contacts)
    monkeypatch.setattr("src.conf.contacts.ContactService.get_contacts", mock_get_contacts)

    response = client.get("/api/contacts/?name=Charlie&surname=Smith", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == len(filtered_contacts)
    assert response.json()[0]["name"] == "Charlie"
    mock_get_contacts.assert_called_once_with("Charlie", "Smith", "", 0, 100, user_data)

@pytest.mark.asyncio
async def test_get_contacts_pagination(client, monkeypatch, headers):
    paginated_contacts = [
        {
            "id": 3,
            "name": "Emma",
            "surname": "White",
            "email": "emma.white@example.com",
            "phone": "555-666-7777",
            "birthday": "1988-11-30",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    ]
    mock_get_contacts = AsyncMock(return_value=paginated_contacts)
    monkeypatch.setattr("src.conf.contacts.ContactService.get_contacts", mock_get_contacts)

    response = client.get("/api/contacts/?skip=2&limit=1", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == len(paginated_contacts)
    assert response.json()[0]["id"] == 3
    mock_get_contacts.assert_called_once_with("", "", "", 2, 1, user_data)

@pytest.mark.asyncio
async def test_get_contact_success(client, monkeypatch, headers):
    contact = contacts[0]
    mock_get_contact = AsyncMock(return_value=contact)
    monkeypatch.setattr("src.conf.contacts.ContactService.get_contact", mock_get_contact)

    response = client.get("/api/contacts/1", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == contact["id"]
    assert response.json()["name"] == contact["name"]
    mock_get_contact.assert_called_once_with(1, user_data)

@pytest.mark.asyncio
async def test_get_contact_not_found(client, monkeypatch, headers):
    mock_get_contact = AsyncMock(return_value=None)
    monkeypatch.setattr("src.conf.contacts.ContactService.get_contact", mock_get_contact)

    response = client.get("/api/contacts/777", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
    mock_get_contact.assert_called_once_with(777, user_data)

@pytest.mark.asyncio
async def test_create_contact_success(client, monkeypatch, headers):
    new_contact = contacts[0]
    mock_create_contact = AsyncMock(return_value=new_contact)
    monkeypatch.setattr("src.conf.contacts.ContactService.create_contact", mock_create_contact)

    response = client.post("/api/contacts/", json=payload, headers=headers)

    expected_contact = ContactModel(**payload)
    assert response.status_code == 201
    assert response.json()["id"] == new_contact["id"]
    mock_create_contact.assert_called_once_with(expected_contact, user_data)

@pytest.mark.asyncio
async def test_create_contact_invalid_data(client, headers):
    invalid_payload = {"name": ""}
    response = client.post("/api/contacts/", json=invalid_payload, headers=headers)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_update_contact_success(client, monkeypatch, headers):
    updated_contact = {**contacts[0], "name": "UpdatedCharlie", "surname": "UpdatedSmith"}
    mock_update_contact = AsyncMock(return_value=updated_contact)
    monkeypatch.setattr("src.conf.contacts.ContactService.update_contact", mock_update_contact)

    update_payload = {
        "name": "UpdatedCharlie",
        "surname": "UpdatedSmith",
        "birthday": "1990-03-15",
        "email": "charlie.smith@example.com",
        "phone": "123-456-7890",
    }

    response = client.put(f"/api/contacts/{contacts[0]['id']}", json=update_payload, headers=headers)
    expected_contact = ContactModel(**update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedCharlie"
    mock_update_contact.assert_called_once_with(contacts[0]["id"], expected_contact, user_data)

@pytest.mark.asyncio
async def test_update_contact_not_found(client, monkeypatch, headers):
    mock_update_contact = AsyncMock(return_value=None)
    monkeypatch.setattr("src.conf.contacts.ContactService.update_contact", mock_update_contact)

    payload = {
        "name": "NonExistent",
        "surname": "Contact",
        "birthday": "1990-03-15",
        "email": "nonexistent@example.com",
        "phone": "000-000-0000",
    }
    response = client.put("/api/contacts/777", json=payload, headers=headers)
    expected_contact = ContactModel(**payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
    mock_update_contact.assert_called_once_with(777, expected_contact, user_data)

@pytest.mark.asyncio
async def test_update_contact_invalid_data(client, headers):
    invalid_payload = {"name": ""}
    response = client.put("/api/contacts/1", json=invalid_payload, headers=headers)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_delete_contact_success(client, monkeypatch, headers):
    mock_delete_contact = AsyncMock(return_value=contacts[0])
    monkeypatch.setattr("src.conf.contacts.ContactService.remove_contact", mock_delete_contact)

    response = client.delete(f"/api/contacts/{contacts[0]['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json() == contacts[0]
    mock_delete_contact.assert_called_once_with(contacts[0]['id'], user_data)

@pytest.mark.asyncio
async def test_delete_contact_not_found(client, monkeypatch, headers):
    mock_delete_contact = AsyncMock(return_value=None)
    monkeypatch.setattr("src.conf.contacts.ContactService.remove_contact", mock_delete_contact)

    response = client.delete("/api/contacts/777", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
    mock_delete_contact.assert_called_once_with(777, user_data)

@pytest.mark.asyncio
async def test_delete_contact_unauthenticated(client):
    app.dependency_overrides.clear()
    response = client.delete(f"/api/contacts/{contacts[0]['id']}")
    assert response.status_code == 401
    assert response.json()["detail"] in ["Not authenticated", "Could not validate credentials"]
