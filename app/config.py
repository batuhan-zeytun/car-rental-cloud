import os


def _truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///car_rental.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_NAME = os.getenv("APP_NAME", "Car Rental Cloud")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    APP_ENV = os.getenv("APP_ENV", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    REDIS_URL = os.getenv("REDIS_URL", "")

    AUTO_CREATE_DB = _truthy("AUTO_CREATE_DB", "true")
    SEED_SAMPLE_DATA = _truthy("SEED_SAMPLE_DATA", "true")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "30"))
