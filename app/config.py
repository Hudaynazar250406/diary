import os


class Config:
    """Базовая конфигурация приложения."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://studenttrack:studenttrack@localhost:5432/studenttrack",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    APP_PORT = int(os.getenv("APP_PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
