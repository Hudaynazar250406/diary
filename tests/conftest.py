import os
import tempfile

import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    """Одноразовая PostgreSQL в CI или временная SQLite локально."""
    database_url = os.getenv("TEST_DATABASE_URL")
    db_path = None
    if not database_url:
        db_fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(db_fd)
        database_url = f"sqlite:///{db_path}"

    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
        SQLALCHEMY_DATABASE_URI = database_url

    test_app = create_app(TestConfig)
    try:
        with test_app.app_context():
            db.create_all()
            try:
                yield test_app
            finally:
                db.session.remove()
                db.drop_all()
                db.session.remove()
                db.engine.dispose()
    finally:
        if db_path and os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def anonymous_client(app):
    """Неавторизованный тестовый клиент."""
    return app.test_client()


@pytest.fixture
def make_user_client(app):
    """Создаёт авторизованный клиент с указанной ролью."""
    counter = {"value": 0}

    def create_client(role, student_id=None, username=None, email=None):
        counter["value"] += 1
        number = counter["value"]
        if username is None:
            username = f"{role}_{number}"
        if email is None:
            email = f"{role}_{number}@example.com"
        with app.app_context():
            user = User(username=username, email=email, role=role, student_id=student_id)
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        test_client = app.test_client()
        with test_client.session_transaction() as session:
            session["user_id"] = user_id
        return test_client
    return create_client


@pytest.fixture
def client(make_user_client):
    """Авторизованный администратор для обычных CRUD-тестов."""
    return make_user_client(User.ROLE_ADMIN, username="test_admin", email="test_admin@example.com")


@pytest.fixture
def teacher_client(make_user_client):
    """Авторизованный преподаватель."""
    return make_user_client(User.ROLE_TEACHER)


@pytest.fixture
def student_client(make_user_client):
    """Авторизованный студент без привязки к записи Student."""
    return make_user_client(User.ROLE_STUDENT)
