from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.user import UserCreate, Token, User, RequestEmail, ResetPassword
from src.conf.email import send_confirm_email, send_reset_password_email
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_password_from_token,
)
from src.services.users import UserService
from src.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
        Registration of a new user.

        Parameters:
        - user_data (UserCreate): Data of the new user.
        - background_tasks (BackgroundTasks): Object for executing background tasks.
        - request (Request): Request for obtaining the base URL.
        - db (AsyncSession): Database session.

        Returns:
        - User: Data of the registered user.

        Raises:
        - HTTPException (409): If a user with the same email or username already exists.
    """
    user_service = UserService(db)
    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this name already exists.",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_confirm_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    User authorization.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): Data for authorization.
    - db (AsyncSession): Database session.

    Returns:
    - Token: JWT access token.

    Raises:
    - HTTPException (401): If the login or password is incorrect, or the email is not verified.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified.",
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Email confirmation for the user.

    Parameters:
    - token (str): Confirmation token.
    - db (AsyncSession): Database session.

    Returns:
    - dict: Message of successful confirmation.

    Raises:
    - HTTPException (400): If the token is invalid or the user is not found.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already verified."}
    await user_service.confirmed_email(email)
    return {"message": "Email has been verified."}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Sending email confirmation to the user.

    Parameters:
    - body (RequestEmail): Data for the request (user's email).
    - background_tasks (BackgroundTasks): Object for executing background tasks.
    - request (Request): Request for obtaining the base URL.
    - db (AsyncSession): Database session.

    Returns:
    - dict: Message about the sent request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_confirm_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}


@router.post("/reset_password")
async def reset_password_request(
    body: ResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Password reset request.

    Parameters:
    - body (ResetPassword): Data for the request (email and new password).
    - background_tasks (BackgroundTasks): Object for executing background tasks.
    - request (Request): Request for obtaining the base URL.
    - db (AsyncSession): Database session.

    Returns:
    - dict: Message about the sent request.

    Raises:
    - HTTPException (400): If the email is not verified.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user:
        return {"message": "Check your email for confirmation."}
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your email is not verified.",
        )
    hashed_password = Hash().get_password_hash(body.password)
    reset_token = await create_access_token(
        data={"sub": user.email, "password": hashed_password}
    )
    background_tasks.add_task(
        send_reset_password_email,
        to_email=body.email,
        username=user.username,
        host=str(request.base_url),
        reset_token=reset_token,
    )
    return {"message": "Check your email for verification."}


@router.get("/confirm_reset_password/{token}")
async def confirm_reset_password(token: str, db: AsyncSession = Depends(get_db)):
    """
    Password reset confirmation.

    Parameters:
    - token (str): Password reset confirmation token.
    - db (AsyncSession): Database session.

    Returns:
    - dict: Message of successful password reset.

    Raises:
    - HTTPException (400): If the token is invalid.
    - HTTPException (404): If the user is not found.
    """
    email = await get_email_from_token(token)
    hashed_password = await get_password_from_token(token)
    if not email or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token.",
        )
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email address not found",
        )
    await user_service.reset_password(user.id, hashed_password)
    return {"message": "Password successfully changed."}
