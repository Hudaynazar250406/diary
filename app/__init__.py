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
from app.routes.auth import auth_bp
from app.routes.web import web_bp
from app.routes.me import me_bp
from app.routes.admin import admin_bp
from app.commands import register_commands
from app.routes.schedules import schedules_bp


def create_app(config_class=Config):
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
    app.register_blueprint(schedules_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)

    app.register_blueprint(me_bp)

    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    register_commands(app)

    return app
