from flask import jsonify
from sqlalchemy.exc import IntegrityError

from app.extensions import db


def register_error_handlers(app):
    """Единый формат ошибок: {"error": "..."}."""

    @app.errorhandler(400)
    def bad_request(error):
        message = getattr(error, "description", "Bad request")
        return jsonify({"error": message}), 400

    @app.errorhandler(403)
    def forbidden(error):
        message = getattr(error, "description", "Forbidden")
        return jsonify({"error": message}), 403

    @app.errorhandler(404)
    def not_found(error):
        message = getattr(error, "description", "Resource not found")
        return jsonify({"error": message}), 404

    @app.errorhandler(409)
    def conflict(error):
        message = getattr(error, "description", "Conflict")
        return jsonify({"error": message}), 409

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        # Откат сессии, чтобы приложение не «залипло» после ошибки
        db.session.rollback()
        return jsonify({"error": "Integrity constraint violation"}), 409

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
