from enum import Enum
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Column,
    ForeignKey,
    func,
    Enum as SqlEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class UserRole(str, Enum):
    """
    Enumeration of user roles.

    Values:
    - USER: Regular user.
    - ADMIN: Administrator.
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Model for the 'contacts' table.

    Attributes:
    - id: Primary key.
    - name: Contact's first name (required).
    - surname: Contact's last name (required).
    - email: Contact's email (unique, required).
    - phone: Contact's phone number (unique, required).
    - birthday: Contact's birthdate (required).
    - created_at: Record creation date (automatic).
    - updated_at: Last record update date (automatic).
    - info: Additional information about the contact.
    - user_id: Foreign key for linking to the user.
    - user: Relationship to the User model.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    info = Column(String(500), nullable=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="contacts")


class User(Base):
    """
    Model for the 'users' table.

    Attributes:
    - id: Primary key.
    - username: Unique username.
    - email: Unique email address.
    - hashed_password: Hashed password.
    - created_at: Record creation date (automatic).
    - avatar: URL of the user's avatar.
    - confirmed: Whether the user is confirmed.
    - role: User role (USER or ADMIN).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
