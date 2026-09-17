from flask import jsonify


def register_error_handlers(app):
    """Единый формат ошибок для всего приложения: {"error": "..."}."""

    @app.errorhandler(400)
    def bad_request(error):
        message = getattr(error, "description", "Bad request")
        return jsonify({"error": message}), 400

    @app.errorhandler(403)
    def forbidden(error):
        message = getattr(
            error,
            "description",
            "Forbidden",
        )

        return jsonify({"error": message}), 403

    @app.errorhandler(404)
    def not_found(error):
        message = getattr(error, "description", "Resource not found")
        return jsonify({"error": message}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500