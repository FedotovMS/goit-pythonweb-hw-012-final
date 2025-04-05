from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.entity.models import User
from src.repository.users import UserRepository
from src.schemas.user import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initializes the service for working with users.

        Arguments:
            db: The asynchronous database session object.
        """
        # Initializes the repository for working with users.
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate) -> User:
        """
        Creates a new user.

        Creates an avatar for the user using Gravatar, and then creates
        the user in the database.

        Arguments:
            body: The user data for creating a new record.

        Returns:
            User: The created user.
        """
        # Creates an avatar using Gravatar.
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            # Logs an error if there is an issue with Gravatar.
            print(e)

        # Creates a user in the database through the repository.
        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Отримує користувача за його ID.

        Аргументи:
            user_id: ID користувача.

        Повертає:
            User або None: Знайдений користувач або None, якщо користувача не знайдено.
        """
        # Retrieves a user by their ID.
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieves a user by their username.

        Arguments:
            username: The user's username.

        Returns:
            User or None: The found user or None if the user is not found.
        """
        # Retrieves a user by their username.
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email.

        Arguments:
            email: The user's email address.

        Returns:
            User or None: The found user or None if the user is not found.
        """
        # Retrieves a user by email
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Confirms the user's email.

        Arguments:
            email: The user's email address.

        Returns:
            None
        """
        # Confirms the user's email.
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Updates the user's avatar URL.

        Arguments:
            email: The user's email address.
            url: The new URL for the avatar.

        Returns:
            User: The updated user.
        """
        # Updates the user's avatar URL.
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str) -> User:
        """
        Resets the user's password.

        Arguments:
            user_id: The user's ID.
            password: The new password for the user.

        Returns:
            User: The updated user.
        """
        # Resets the user's password.
        return await self.repository.reset_password(user_id, password)
