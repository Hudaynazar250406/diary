from flask import Blueprint, request, jsonify, abort
from app.extensions import db
from app.models.discipline import Discipline

disciplines_bp = Blueprint("disciplines", __name__)


@disciplines_bp.route("/disciplines", methods=["GET"])
def get_disciplines():
    """Список всех дисциплин."""
    disciplines = Discipline.query.all()
    return jsonify([d.to_dict() for d in disciplines]), 200


@disciplines_bp.route("/disciplines/<int:discipline_id>", methods=["GET"])
def get_discipline(discipline_id):
    """Получение дисциплины по ID."""
    discipline = db.session.get(Discipline, discipline_id)
    if not discipline:
        abort(404, description="Дисциплина не найдена")
    return jsonify(discipline.to_dict()), 200


@disciplines_bp.route("/disciplines", methods=["POST"])
def create_discipline():
    """Создание новой дисциплины."""
    data = request.get_json(silent=True)
    
    if not data:
        abort(400, description="Тело запроса не может быть пустым")
    if "discipline_name" not in data:
        abort(400, description="Поле 'discipline_name' обязательно")
    if not data["discipline_name"].strip():
        abort(400, description="Название дисциплины не может быть пустым")

    discipline = Discipline(discipline_name=data["discipline_name"].strip())
    db.session.add(discipline)
    db.session.commit()
    return jsonify(discipline.to_dict()), 201


@disciplines_bp.route("/disciplines/<int:discipline_id>", methods=["PUT"])
def update_discipline(discipline_id):
    """Обновление дисциплины."""
    discipline = db.session.get(Discipline, discipline_id)
    if not discipline:
        abort(404, description="Дисциплина не найдена")

    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Тело запроса не может быть пустым")
    if "discipline_name" not in data:
        abort(400, description="Поле 'discipline_name' обязательно")
    if not data["discipline_name"].strip():
        abort(400, description="Название дисциплины не может быть пустым")

    discipline.discipline_name = data["discipline_name"].strip()
    db.session.commit()
    return jsonify(discipline.to_dict()), 200


@disciplines_bp.route("/disciplines/<int:discipline_id>", methods=["DELETE"])
def delete_discipline(discipline_id):
    """Удаление дисциплины."""
    discipline = db.session.get(Discipline, discipline_id)
    if not discipline:
        abort(404, description="Дисциплина не найдена")

    db.session.delete(discipline)
    db.session.commit()
    return jsonify({"message": "Дисциплина удалена"}), 200