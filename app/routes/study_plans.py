from flask import Blueprint, request, jsonify, abort
from app.extensions import db
from app.models.study_plan import StudyPlan
from app.models.group import Group
from app.models.discipline import Discipline

study_plans_bp = Blueprint("study_plans", __name__)


@study_plans_bp.route("/study_plans", methods=["GET"])
def get_study_plans():
    """Получение списка всех учебных планов."""
    plans = StudyPlan.query.all()
    return jsonify([p.to_dict() for p in plans]), 200


@study_plans_bp.route("/study_plans/<int:plan_id>", methods=["GET"])
def get_study_plan(plan_id):
    """Получение учебного плана по ID."""
    plan = db.session.get(StudyPlan, plan_id)
    if not plan:
        abort(404, description="Учебный план не найден")
    return jsonify(plan.to_dict()), 200


@study_plans_bp.route("/study_plans", methods=["POST"])
def create_study_plan():
    """Создание нового учебного плана с проверкой группы и дисциплины."""
    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Тело запроса не может быть пустым")

    required = ["group_id", "discipline_id", "semester"]
    missing = [f for f in required if f not in data]
    if missing:
        abort(400, description=f"Отсутствуют обязательные поля: {missing}")

    if not isinstance(data["semester"], int) or data["semester"] < 1:
        abort(400, description="Поле 'semester' должно быть целым числом >= 1")

    group = db.session.get(Group, data["group_id"])
    if not group:
        abort(400, description="Указанная группа не найдена")

    discipline = db.session.get(Discipline, data["discipline_id"])
    if not discipline:
        abort(400, description="Указанная дисциплина не найдена")

    plan = StudyPlan(
        group_id=data["group_id"],
        discipline_id=data["discipline_id"],
        semester=data["semester"],
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201


@study_plans_bp.route("/study_plans/<int:plan_id>", methods=["PUT"])
def update_study_plan(plan_id):
    """Обновление учебного плана."""
    plan = db.session.get(StudyPlan, plan_id)
    if not plan:
        abort(404, description="Учебный план не найден")

    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Тело запроса не может быть пустым")

    if "group_id" in data:
        group = db.session.get(Group, data["group_id"])
        if not group:
            abort(400, description="Указанная группа не найдена")
        plan.group_id = data["group_id"]

    if "discipline_id" in data:
        discipline = db.session.get(Discipline, data["discipline_id"])
        if not discipline:
            abort(400, description="Указанная дисциплина не найдена")
        plan.discipline_id = data["discipline_id"]

    if "semester" in data:
        if not isinstance(data["semester"], int) or data["semester"] < 1:
            abort(400, description="Поле 'semester' должно быть целым числом >= 1")
        plan.semester = data["semester"]

    db.session.commit()
    return jsonify(plan.to_dict()), 200


@study_plans_bp.route("/study_plans/<int:plan_id>", methods=["DELETE"])
def delete_study_plan(plan_id):
    """Удаление учебного плана."""
    plan = db.session.get(StudyPlan, plan_id)
    if not plan:
        abort(404, description="Учебный план не найден")

    db.session.delete(plan)
    db.session.commit()
    return jsonify({"message": "Учебный план удалён"}), 200