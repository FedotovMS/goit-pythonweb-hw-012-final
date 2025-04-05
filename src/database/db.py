import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Class for managing asynchronous database sessions.

    This class creates an asynchronous engine and session maker for working with the database.

    Attributes:
    - _engine (AsyncEngine): Asynchronous engine for connecting to the database.
    - _session_maker (async_sessionmaker): Factory for creating sessions.

    Methods:
    - session: Context manager for working with a database session.

    Usage example:
    ```
    """

    def __init__(self, url: str):
        """
        Initializes the engine and session factory for the database.

        Parameters:
        - url (str): URL for connecting to the database.
        """
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Context manager for creating and managing a database session.

        Raises:
        - Exception: If the session factory is not initialized.
        - SQLAlchemyError: If an error occurs while working with the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


# Ініціалізація менеджера сесій
sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Generator for obtaining a database session in FastAPI dependencies.

    Usage example:
    ```
    @router.get("/")
    async def example_endpoint(db: AsyncSession = Depends(get_db)):
        # Use db for database operations
    ```
    """
    async with sessionmanager.session() as session:
        yield session
