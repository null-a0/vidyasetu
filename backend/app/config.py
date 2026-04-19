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

    # ----- AI / Gemini -----
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-3.1-flash-lite-preview"
    GEMINI_API_BASE_URL: str = "https://generativelanguage.googleapis.com"
    GEMINI_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_RETRIES: int = 3
    AI_RETRY_BASE_DELAY_SECONDS: float = 0.5
    AI_ADMIN_REPORT_CACHE_TTL_SECONDS: int = 3600
    AI_ADMIN_REPORT_PROMPT_VERSION: str = "v1"
    AI_ADMIN_REPORT_USER_RATE_LIMIT: int = 3
    AI_ADMIN_REPORT_INSTITUTION_RATE_LIMIT: int = 10
    AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS: int = 600
    AI_ADMIN_REPORT_STALE_AFTER_SECONDS: int = 900
    AI_STUDENT_EXPLANATION_PROMPT_VERSION: str = "v1"
    AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS: int = 86400
    AI_STUDENT_EXPLANATION_USER_RATE_LIMIT: int = 12
    AI_STUDENT_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS: int = 600
    AI_STUDENT_EXPLANATION_STALE_AFTER_SECONDS: int = 900
    # "database" is safe for multi-instance deployments sharing the primary DB.
    # "memory" is per-process and should be used only for local/dev.
    AI_RATE_LIMIT_BACKEND: str = "database"
    AI_RATE_LIMIT_COUNTER_RETENTION_SECONDS: int = 86400

    # ----- Redis / Celery (Async jobs) -----
    # Upstash typically uses rediss:// (TLS). Example:
    # rediss://:<password>@<host>:<port>
    REDIS_URL: str = "rediss://default:gQAAAAAAAY6gAAIocDI1YjkxMTQyZDkwY2M0MDVmODdkODg2MDQxYWMxOGRkM3AyMTAyMDQ4@exotic-stud-102048.upstash.io:6379"
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    CELERY_TASK_DEFAULT_QUEUE: str = "vidyasetu"

    AI_JOB_DEDUP_LOCK_TTL_SECONDS: int = 300
    AI_JOB_IDEMPOTENCY_TTL_SECONDS: int = 86400
    AI_JOB_PROGRESS_TTL_SECONDS: int = 3600
    AI_JOB_MAX_RETRIES: int = 5
    SUPPORT_RERUN_LIMIT_PER_DAY: int = 3

    # ----- Scheduled reports -----
    # Scheduler ticks are handled by Celery Beat; this controls how far we look ahead.
    SCHEDULED_REPORT_LOOKAHEAD_SECONDS: int = 120

    # ----- Email (optional) -----
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    @property
    def celery_broker_url(self) -> str:
        return (self.CELERY_BROKER_URL or self.REDIS_URL).strip()

    @property
    def celery_result_backend(self) -> str:
        return (self.CELERY_RESULT_BACKEND or self.REDIS_URL).strip()


settings = Settings()
