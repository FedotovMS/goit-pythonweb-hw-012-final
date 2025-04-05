from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.openapi.models import Contact

from src.entity.models import User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactModel


class ContactService:
    """
    A service for managing a user’s contacts. It allows creating, updating, deleting, and retrieving contacts.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a connection to the database.

        Arguments:
            db: connection to the asynchronous database session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Creates a new contact.

        It checks if a contact with the same email or phone number already exists. If such a contact exists, it raises an error.

        Arguments:
            body: data model for creating the contact.
            user: the current user creating the contact.

        Returns:
            The created contact.

        Raises:
            HTTPException if a contact with the same email or phone number already exists.
        """
        if await self.repository.is_contact_exists(body.email, body.phone, user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone}' phone number already exists.",
            )
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Retrieves a list of contacts with the option to filter by parameters.

        Arguments:
            name: contact's first name for filtering.
            surname: contact's last name for filtering.
            email: contact's email for filtering.
            skip: the number of contacts to skip (pagination).
            limit: the maximum number of contacts to retrieve.
            user: the current user to check access to contacts.

        Returns:
            A list of contacts that satisfy the filtering conditions.
        """
        return await self.repository.get_contacts(
            name, surname, email, skip, limit, user
        )

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieves a contact by its ID.

        Arguments:
            contact_id: the unique identifier of the contact.
            user: the current user to check access to the contact.

        Returns:
            The contact or None if the contact is not found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact:
        """
        Updates the contact data by its ID.

        Arguments:
            contact_id: the unique identifier of the contact.
            body: new data for updating the contact.
            user: the current user to check access to the contact.

        Returns:
            The updated contact.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact:
        """
        Deletes a contact by its ID.

        Arguments:
            contact_id: the unique identifier of the contact.
            user: the current user to check access to the contact.

        Returns:
            The deleted contact.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def get_upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Retrieves a list of contacts with upcoming birthdays (by number of days).

        Arguments:
            days: the number of days to filter the upcoming birthdays.
            user: the current user to check access to the contacts.

        Returns:
            A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays(days, user)
