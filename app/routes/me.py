from flask import Blueprint, abort, g, jsonify

from app.models.discipline import Discipline
from app.models.grade import Grade
from app.models.schedule import Schedule
from app.models.study_plan import StudyPlan
from app.models.user import User
from app.permissions import role_required
from app.extensions import db


me_bp = Blueprint(
    "me",
    __name__,
    url_prefix="/me",
)


def get_current_student():
    if g.user.student_id is None:
        abort(
            400,
            description="Аккаунт не привязан к студенту",
        )

    return g.user.student


@me_bp.get("/grades")
@role_required(User.ROLE_STUDENT)
def my_grades():
    student = get_current_student()

    grades = Grade.query.filter_by(
        student_id=student.id,
    ).all()

    result = []

    for grade in grades:
        result.append(
            {
                "id": grade.id,
                "discipline_id": grade.discipline_id,
                "discipline_name": grade.discipline.discipline_name,
                "grade": grade.grade,
                "date": grade.date.isoformat(),
            }
        )

    return jsonify(result), 200


@me_bp.get("/disciplines")
@role_required(User.ROLE_STUDENT)
def my_disciplines():
    student = get_current_student()

    plans = StudyPlan.query.filter_by(
        group_id=student.group_id,
    ).order_by(
        StudyPlan.semester.asc(),
    ).all()

    result = []

    for plan in plans:
        discipline = db.session.get(
            Discipline,
            plan.discipline_id,
        )

        result.append(
            {
                "id": discipline.id,
                "discipline_name": discipline.discipline_name,
                "semester": plan.semester,
            }
        )

    return jsonify(result), 200


@me_bp.get("/schedule")
@role_required(User.ROLE_STUDENT)
def my_schedule():
    student = get_current_student()

    lessons = Schedule.query.filter_by(
        group_id=student.group_id,
    ).order_by(
        Schedule.weekday.asc(),
        Schedule.start_time.asc(),
    ).all()

    weekdays = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
        7: "Воскресенье",
    }

    result = []

    for lesson in lessons:
        result.append(
            {
                "id": lesson.id,
                "weekday": lesson.weekday,
                "weekday_name": weekdays[lesson.weekday],
                "discipline_name": lesson.discipline.discipline_name,
                "start_time": lesson.start_time.strftime("%H:%M"),
                "end_time": lesson.end_time.strftime("%H:%M"),
                "room": lesson.room,
            }
        )

    return jsonify(result), 200