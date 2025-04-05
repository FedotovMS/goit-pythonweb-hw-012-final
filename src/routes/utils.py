from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Service health check and database connection verification.

    This endpoint performs a simple query to the database to check if the database is configured correctly
    and whether the application can successfully connect to it.

    Parameters:
    - db (AsyncSession): Asynchronous database session obtained via dependency.

    Returns:
    - dict: Service status message.

    Error cases:
    - 500 INTERNAL_SERVER_ERROR: If the database is not configured or an error occurs during connection.
    """
    try:
        # Performing a test query to the database.
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        # Successful response if the query was executed.
        return {"message": "Welcome to FastAPI!"}

    except Exception as e:
        # Error logging and returning a failure message.
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
