import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация приложения читается из переменных окружения (.env)."""

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///studenttrack.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    APP_PORT = int(os.getenv("APP_PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
