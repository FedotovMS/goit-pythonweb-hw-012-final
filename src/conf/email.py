from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

# Configuration settings for connecting to the email server.
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_confirm_email(to_email: EmailStr, username: str, host: str) -> None:
    """
    Sends an email to confirm the email address.

    Creates a token for email verification and sends an email to the user
    with a link to confirm their email address.

    Arguments:
        to_email: The recipient's email address.
        username: The username for personalizing the email.
        host: The host (base address) used to build the verification link.

    Raises:
        ConnectionErrors: If an error occurs while connecting to the email server.
    """
    try:
        # Creates a token for email verification.
        token_verification = create_email_token({"sub": to_email})
        # Composes a message for sending.
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[to_email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Initializes FastMail and sends the message.
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(
    to_email: EmailStr, username: str, host: str, reset_token: str
) -> None:
    """
    Sends an email for password reset.

    Forms a password reset link and sends an email to the user with instructions
    on how to change their password.

    Arguments:
        to_email: The recipient's email address.
        username: The username for personalizing the email.
        host: The host (base address) used to build the link.
        reset_token: The password reset token added to the link.

    Raises:
        ConnectionErrors: If an error occurs while connecting to the email server.
    """
    try:
        # Composes a password reset link.
        reset_link = f"{host}api/auth/confirm_reset_password/{reset_token}"

        # Composes a message for sending.

        message = MessageSchema(
            subject="Important: Update your account information",
            recipients=[to_email],
            template_body={"reset_link": reset_link, "username": username},
            subtype=MessageType.html,
        )

        # Initializes FastMail and sends the message.
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
