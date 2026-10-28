import os
import secrets


class Config:
    """Базовая конфигурация приложения."""

    # ДОПУЩЕНИЕ: без DATABASE_URL локальный запуск использует SQLite.
    # Compose передаёт PostgreSQL URL с явным драйвером psycopg 3.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///studenttrack.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Для нескольких воркеров обязательно задавать общий SECRET_KEY в окружении.
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    APP_PORT = int(os.getenv("APP_PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
