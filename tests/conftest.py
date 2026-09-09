import os
import tempfile

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Тестовое приложение с изолированной временной SQLite БД."""
    db_fd, db_path = tempfile.mkstemp()

    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        }
    )

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
