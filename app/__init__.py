from flask import Flask

from app.config import Config
from app.extensions import db
from app.errors import register_error_handlers

from app.routes.health import health_bp
from app.routes.disciplines import disciplines_bp
from app.routes.study_plans import study_plans_bp
from app.routes.groups import groups_bp
from app.routes.students import students_bp
from app.routes.grades import grades_bp


def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    register_error_handlers(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(disciplines_bp)
    app.register_blueprint(study_plans_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(grades_bp)

    with app.app_context():
        db.create_all()

    return app
