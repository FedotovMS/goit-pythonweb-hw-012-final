from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.entity.models import UserRole



class User(BaseModel):
    """
    Model for representing a user.

    Attributes:
        id: Unique identifier of the user
        username: Username of the user
        email: Email address of the user
        avatar: URL to the user's avatar
        role: Role of the user (e.g., administrator or user)
    """

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Model for creating a new user.

    Attributes:
        username: Username of the user
        email: Email address of the user
        password: Password of the user (minimum 4 characters, maximum 128 characters)
        role: Role of the user (e.g., administrator or user)
    """

    username: str
    email: str
    password: str = Field(min_length=4, max_length=128)
    role: UserRole


class Token(BaseModel):
    """
    Model for returning the access token.

    Attributes:
        access_token: The access token
        token_type: The type of the token (e.g., Bearer)
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Model for requesting the email for password recovery.

    Attribute:
        email: The user's email address
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    Model for resetting the password.

    Attributes:
        email: The user's email address
        password: The user's new password (minimum 4 characters, maximum 128 characters)
    """

    email: EmailStr
    password: str = Field(min_length=4, max_length=128, description="New Password")
