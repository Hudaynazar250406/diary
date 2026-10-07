import os


class Config:
    """Базовая конфигурация приложения."""

    # ВАЖНО: префикс "+psycopg" указывает SQLAlchemy использовать psycopg 3.
    # Без него SQLAlchemy пытается импортировать psycopg2 (старый драйвер),
    # которого у нас в requirements.txt нет.
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://studenttrack:studenttrack@127.0.0.1:5432/studenttrack?connect_timeout=5",
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    APP_PORT = int(os.getenv("APP_PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"