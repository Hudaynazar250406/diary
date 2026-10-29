import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


class Config:
    """Базовая конфигурация приложения."""

    # ВАЖНО: префикс "+psycopg" указывает SQLAlchemy использовать psycopg 3.
    # Без него SQLAlchemy пытается импортировать psycopg2 (старый драйвер),
    # которого у нас в requirements.txt нет.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or URL.create(
        "postgresql+psycopg",
        username=os.getenv("POSTGRES_USER", "studenttrack"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "studenttrack"),
        query={"connect_timeout": "5"},
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    APP_PORT = int(os.getenv("APP_PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
