from flask import Blueprint, request, jsonify, abort
from app.extensions import db
from app.models.study_plan import StudyPlan
from app.models.group import Group
from app.models.discipline import Discipline

study_plans_bp = Blueprint("study_plans", __name__)

@study_plans_bp.route("/study_plans", methods=["GET"])
def get_study_plans():
    plans = StudyPlan.query.all()
    return jsonify([p.to_dict() for p in plans]), 200

@study_plans_bp.route("/study_plans", methods=["POST"])
def create_study_plan():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Тело запроса пустое")
    
    required = ["group_id", "discipline_id", "semester"]
    missing = [f for f in required if f not in data]
    if missing:
        abort(400, description=f"Нет полей: {missing}")

    if not isinstance(data["semester"], int) or data["semester"] < 1:
        abort(400, description="Семестр должен быть числом >= 1")

    if not db.session.get(Group, data["group_id"]):
        abort(400, description="Группа не найдена")
    if not db.session.get(Discipline, data["discipline_id"]):
        abort(400, description="Дисциплина не найдена")

    plan = StudyPlan(
        group_id=data["group_id"],
        discipline_id=data["discipline_id"],
        semester=data["semester"],
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201