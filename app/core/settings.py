from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # DB
    DATABASE_URL: str

    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "RS256"
    AUTH_COOKIE_NAME: str = "access_token"

    # Encryption
    ENCRYPTION_KEY: str

    # Paths
    MEDIA_ROOT: str = "media"
    STATIC_ROOT: str = "web/static"
    TEMPLATES_ROOT: str = "web/templates"

    # SMTP
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "no-reply@example.com"


settings = Settings()