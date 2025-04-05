from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas.user import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10 per minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Getting information about the currently authorized user.

    Limits:
    - No more than 10 requests per minute.

    Parameters:
    - request (Request): HTTP request to track the limit.
    - user (User): The currently authorized user.

    Returns:
    - User: User data.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updating avatar for the current administrator.

    Parameters:
    - file (UploadFile): Uploaded avatar file.
    - user (User): The currently authorized administrator.
    - db (AsyncSession): Database session.

    Returns:
    - User: Updated user data with the new avatar URL.
    """
    # Upload ava to cloud
    avatar_service = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    )
    avatar_url = avatar_service.upload_file(file, user.username)

    # Update ava's URL in DB
    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
