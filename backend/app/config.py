from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- Database -----
    DATABASE_URL: str = "sqlite+aiosqlite:///./vidyasetu.db"

    # ----- Auth / JWT -----
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # ----- Application -----
    APP_NAME: str = "VidyaSetu"
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8000"   # canonical URL for QR links / emails
    FRONTEND_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]


settings = Settings()
