import datetime

from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.discipline import Discipline
from app.models.group import Group
from app.models.schedule import Schedule
from app.models.study_plan import StudyPlan
from app.models.user import User
from app.permissions import role_required


schedules_bp = Blueprint(
    "schedules",
    __name__,
)


def parse_schedule_data(data, schedule_id=None):
    required = {
        "group_id",
        "discipline_id",
        "weekday",
        "start_time",
        "end_time",
    }

    missing = required - data.keys()

    if missing:
        abort(
            400,
            description=f"Отсутствуют поля: {sorted(missing)}",
        )

    group_id = data["group_id"]
    discipline_id = data["discipline_id"]
    weekday = data["weekday"]

    group = db.session.get(
        Group,
        group_id,
    )

    if group is None:
        abort(
            400,
            description="Группа не найдена",
        )

    discipline = db.session.get(
        Discipline,
        discipline_id,
    )

    if discipline is None:
        abort(
            400,
            description="Дисциплина не найдена",
        )

    if not isinstance(weekday, int) or not 1 <= weekday <= 7:
        abort(
            400,
            description="День недели должен быть от 1 до 7",
        )

    plan = StudyPlan.query.filter_by(
        group_id=group_id,
        discipline_id=discipline_id,
    ).first()

    if plan is None:
        abort(
            400,
            description=(
                "Дисциплина отсутствует "
                "в учебном плане группы"
            ),
        )

    try:
        start_time = datetime.time.fromisoformat(
            data["start_time"],
        )

        end_time = datetime.time.fromisoformat(
            data["end_time"],
        )
    except ValueError:
        abort(
            400,
            description="Время должно быть в формате HH:MM",
        )

    if end_time <= start_time:
        abort(
            400,
            description=(
                "Время окончания должно быть "
                "позже времени начала"
            ),
        )

    conflict_query = Schedule.query.filter(
        Schedule.group_id == group_id,
        Schedule.weekday == weekday,
        Schedule.start_time < end_time,
        Schedule.end_time > start_time,
    )

    if schedule_id is not None:
        conflict_query = conflict_query.filter(
            Schedule.id != schedule_id,
        )

    conflict = conflict_query.first()

    if conflict is not None:
        abort(
            400,
            description=(
                "У этой группы уже есть занятие "
                "в указанное время"
            ),
        )

    return {
        "group_id": group_id,
        "discipline_id": discipline_id,
        "weekday": weekday,
        "start_time": start_time,
        "end_time": end_time,
        "room": data.get("room"),
    }


@schedules_bp.get("/schedules")
@role_required(
    User.ROLE_TEACHER,
    User.ROLE_ADMIN,
)
def get_schedules():
    schedules = Schedule.query.order_by(
        Schedule.weekday.asc(),
        Schedule.start_time.asc(),
    ).all()

    return jsonify(
        [schedule.to_dict() for schedule in schedules]
    ), 200


@schedules_bp.post("/schedules")
@role_required(
    User.ROLE_TEACHER,
    User.ROLE_ADMIN,
)
def create_schedule():
    data = request.get_json(silent=True) or {}

    values = parse_schedule_data(data)

    schedule = Schedule(**values)

    db.session.add(schedule)
    db.session.commit()

    return jsonify(schedule.to_dict()), 201


@schedules_bp.put("/schedules/<int:schedule_id>")
@role_required(
    User.ROLE_TEACHER,
    User.ROLE_ADMIN,
)
def update_schedule(schedule_id):
    schedule = db.session.get(
        Schedule,
        schedule_id,
    )

    if schedule is None:
        abort(
            404,
            description="Занятие не найдено",
        )

    data = request.get_json(silent=True) or {}

    values = parse_schedule_data(
        data,
        schedule_id=schedule.id,
    )

    schedule.group_id = values["group_id"]
    schedule.discipline_id = values["discipline_id"]
    schedule.weekday = values["weekday"]
    schedule.start_time = values["start_time"]
    schedule.end_time = values["end_time"]
    schedule.room = values["room"]

    db.session.commit()

    return jsonify(schedule.to_dict()), 200


@schedules_bp.delete("/schedules/<int:schedule_id>")
@role_required(
    User.ROLE_TEACHER,
    User.ROLE_ADMIN,
)
def delete_schedule(schedule_id):
    schedule = db.session.get(
        Schedule,
        schedule_id,
    )

    if schedule is None:
        abort(
            404,
            description="Занятие не найдено",
        )

    db.session.delete(schedule)
    db.session.commit()

    return "", 204