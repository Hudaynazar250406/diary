from flask import Blueprint, request, jsonify, abort

from app.extensions import db
from app.models.grade import Grade
from app.models.student import Student
from app.models.discipline import Discipline
from app.models.study_plan import StudyPlan


grades_bp = Blueprint("grades", __name__)


def validate_grade_value(value):
    if type(value) is not int or value < 1 or value > 5:
        abort(400, description="Оценка должна быть целым числом от 1 до 5")


def get_student_or_404(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        abort(404, description="Студент не найден")

    return student


def get_discipline_or_404(discipline_id):
    discipline = db.session.get(Discipline, discipline_id)

    if not discipline:
        abort(404, description="Дисциплина не найдена")

    return discipline


def validate_study_plan(student, discipline_id):
    study_plan = StudyPlan.query.filter_by(
        group_id=student.group_id,
        discipline_id=discipline_id,
    ).first()

    if not study_plan:
        abort(
            400,
            description="Дисциплина отсутствует в учебном плане группы студента",
        )


@grades_bp.route("/grades", methods=["GET"])
def get_grades():
    # Получение списка всех оценок
    grades = Grade.query.all()
    return jsonify([grade.to_dict() for grade in grades]), 200


@grades_bp.route("/grades/<int:grade_id>", methods=["GET"])
def get_grade(grade_id):
    # Получение оценки по ID
    grade = db.session.get(Grade, grade_id)

    if not grade:
        abort(404, description="Оценка не найдена")

    return jsonify(grade.to_dict()), 200


@grades_bp.route("/grades", methods=["POST"])
def create_grade():
    # Создание новой оценки
    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Тело запроса не может быть пустым")

    required = ["student_id", "discipline_id", "grade"]
    missing = [field for field in required if field not in data]

    if missing:
        abort(400, description=f"Отсутствуют обязательные поля: {missing}")

    validate_grade_value(data["grade"])

    student = get_student_or_404(data["student_id"])
    get_discipline_or_404(data["discipline_id"])

    validate_study_plan(student, data["discipline_id"])

    grade = Grade(
        student_id=data["student_id"],
        discipline_id=data["discipline_id"],
        grade=data["grade"],
    )

    db.session.add(grade)
    db.session.commit()

    return jsonify(grade.to_dict()), 201


@grades_bp.route("/grades/<int:grade_id>", methods=["PUT"])
def update_grade(grade_id):
    # Обновление существующей оценки
    grade = db.session.get(Grade, grade_id)

    if not grade:
        abort(404, description="Оценка не найдена")

    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Тело запроса не может быть пустым")

    student_id = data.get("student_id", grade.student_id)
    discipline_id = data.get("discipline_id", grade.discipline_id)
    grade_value = data.get("grade", grade.grade)

    validate_grade_value(grade_value)

    student = get_student_or_404(student_id)
    get_discipline_or_404(discipline_id)

    validate_study_plan(student, discipline_id)

    grade.student_id = student_id
    grade.discipline_id = discipline_id
    grade.grade = grade_value

    db.session.commit()

    return jsonify(grade.to_dict()), 200


@grades_bp.route("/grades/<int:grade_id>", methods=["DELETE"])
def delete_grade(grade_id):
    # Удаление оценки
    grade = db.session.get(Grade, grade_id)

    if not grade:
        abort(404, description="Оценка не найдена")

    db.session.delete(grade)
    db.session.commit()

    return jsonify({"message": "Оценка удалена"}), 200
