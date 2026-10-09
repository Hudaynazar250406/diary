import socket

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    """Служебный эндпоинт проверки работоспособности приложения.

    Поле ``instance`` — hostname контейнера: позволяет убедиться, что запросы
    распределяются между несколькими экземплярами приложения за балансировщиком.
    """
    return jsonify({
        "status": "ok",
        "instance": socket.gethostname(),
    }), 200
