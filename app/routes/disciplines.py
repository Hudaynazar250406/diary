from flask import Blueprint, request, jsonify, abort
from app.extensions import db
from app.models.discipline import Discipline

disciplines_bp = Blueprint("disciplines", __name__)

@disciplines_bp.route("/disciplines", methods=["GET"])
def get_disciplines():
    disciplines = Discipline.query.all()
    return jsonify([d.to_dict() for d in disciplines]), 200

@disciplines_bp.route("/disciplines", methods=["POST"])
def create_discipline():
    data = request.get_json(silent=True)
    
    # Валидация (проверка на ошибки)
    if not data:
        abort(400, description="Тело запроса не может быть пустым")
    if "discipline_name" not in data:
        abort(400, description="Поле 'discipline_name' обязательно")
    if not data["discipline_name"].strip():
        abort(400, description="Название дисциплины не может быть пустым")

    # Сохранение в БД
    discipline = Discipline(discipline_name=data["discipline_name"].strip())
    db.session.add(discipline)
    db.session.commit()
    
    return jsonify(discipline.to_dict()), 201