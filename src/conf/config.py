from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration class for application settings.

    This class automatically loads settings from the environment or a `.env` file using the Pydantic library.

    Attributes:
    - DB_URL (str): URL for connecting to the database.
    - JWT_SECRET (str): Secret key for signing JWT tokens.
    - JWT_ALGORITHM (str): Algorithm for generating JWT tokens (default: HS256).
    - JWT_EXPIRATION_SECONDS (int): Token lifetime in seconds (default: 3600).
    - MAIL_USERNAME (EmailStr): SMTP server login.
    - MAIL_PASSWORD (str): SMTP server password.
    - MAIL_FROM (EmailStr): Email address from which emails are sent.
    - MAIL_PORT (int): Port for connecting to the SMTP server.
    - MAIL_SERVER (str): SMTP server domain name.
    - MAIL_FROM_NAME (str): Sender name for emails (default: "API Service").
    - MAIL_STARTTLS (bool): Whether to use STARTTLS for SMTP (default: False).
    - MAIL_SSL_TLS (bool): Whether to use SSL/TLS for SMTP (default: True).
    - USE_CREDENTIALS (bool): Whether to use credentials for SMTP (default: True).
    - VALIDATE_CERTS (bool): Whether to validate SSL certificates (default: True).
    - CLOUDINARY_NAME (str): Cloudinary account name.
    - CLOUDINARY_API_KEY (int): API key for Cloudinary.
    - CLOUDINARY_API_SECRET (str): Secret key for Cloudinary.

    Methods:
    - model_config: Configuration for loading settings from the `.env` file.

    Usage example:
    ```
    from src.conf.config import settings
    print(settings.DB_URL)
    ```
    """

    DB_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Initialization of the settings object
settings = Settings()
