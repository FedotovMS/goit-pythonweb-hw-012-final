from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactModel(BaseModel):
    """
    Model for creating or updating a contact.

    Attributes:
        name: Contact's first name (minimum 2 characters, maximum 50 characters)
        surname: Contact's last name (minimum 2 characters, maximum 50 characters)
        email: Contact's email address (minimum 7 characters, maximum 100 characters)
        phone: Contact's phone number (minimum 7 characters, maximum 20 characters)
        birthday: Contact's birth date
        info: Additional information about the contact (optional)
    """

    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(min_length=7, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    birthday: date
    info: Optional[str] = None


class ContactResponse(ContactModel):
    """
    Model for the response when retrieving a contact from the database.

    Attributes:
        id: Unique identifier of the contact
        created_at: Date and time when the contact was created
        updated_at: Date and time when the contact was last updated (optional)
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

