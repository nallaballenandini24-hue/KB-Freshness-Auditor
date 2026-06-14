"""Application configuration settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables"""

    # Application
    APP_NAME: str = "KB Freshness Auditor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/kb_auditor"
    DB_ECHO: bool = False

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "kb-articles"

    # Groq API
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"

    # Temporal
    TEMPORAL_HOST: str = "localhost"
    TEMPORAL_PORT: int = 7233
    TEMPORAL_NAMESPACE: str = "default"

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_WORKERS: int = 4

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Freshness Scoring
    ARTICLE_AGE_WEIGHT: float = 0.5
    TICKET_COUNT_WEIGHT: float = 0.3
    DAYS_SINCE_UPDATE_WEIGHT: float = 0.2

    # Thresholds
    FRESH_THRESHOLD: float = 30.0
    WARNING_THRESHOLD: float = 60.0
    STALE_THRESHOLD: float = 100.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
