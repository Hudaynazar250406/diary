from flask import Flask

from app.config import Config
from app.extensions import db
from app.errors import register_error_handlers
from app.routes.health import health_bp


def create_app():
    """Flask application factory.

    Собирает приложение: применяет конфигурацию, инициализирует расширения
    (SQLAlchemy), регистрирует обработчики ошибок и blueprint'ы маршрутов.
    Модели предметной области (Student, Group, Discipline, StudyPlan, Grade)
    будут подключаться сюда по мере реализации соответствующих задач.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    register_error_handlers(app)

    app.register_blueprint(health_bp)

    with app.app_context():
        db.create_all()

    return app
