from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.student import Student
from app.models.user import User
from app.permissions import role_required


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


@admin_bp.get("/users")
@role_required(User.ROLE_ADMIN)
def list_users():
    users = User.query.order_by(
        User.id.asc(),
    ).all()

    return jsonify(
        [user.to_dict() for user in users]
    ), 200


@admin_bp.put("/users/<int:user_id>/role")
@role_required(User.ROLE_ADMIN)
def update_user_role(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(
            404,
            description="Пользователь не найден",
        )

    if user.role == User.ROLE_ADMIN:
        abort(
            400,
            description=(
                "Роль администратора изменяется "
                "только через CLI"
            ),
        )

    data = request.get_json(silent=True) or {}
    role = data.get("role")

    allowed_roles = {
        User.ROLE_STUDENT,
        User.ROLE_TEACHER,
    }

    if role not in allowed_roles:
        abort(
            400,
            description="Недопустимая роль",
        )

    user.role = role

    if role != User.ROLE_STUDENT:
        user.student_id = None

    db.session.commit()

    return jsonify(user.to_dict()), 200


@admin_bp.put("/users/<int:user_id>/student")
@role_required(User.ROLE_ADMIN)
def update_user_student(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(
            404,
            description="Пользователь не найден",
        )

    if user.role != User.ROLE_STUDENT:
        abort(
            400,
            description=(
                "Привязать запись студента можно "
                "только к пользователю с ролью student"
            ),
        )

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")

    if student_id is None:
        user.student_id = None
        db.session.commit()

        return jsonify(user.to_dict()), 200

    student = db.session.get(
        Student,
        student_id,
    )

    if student is None:
        abort(
            404,
            description="Студент не найден",
        )

    existing_user = User.query.filter(
        User.student_id == student.id,
        User.id != user.id,
    ).first()

    if existing_user is not None:
        abort(
            400,
            description=(
                "Этот студент уже привязан "
                "к другому аккаунту"
            ),
        )

    user.student_id = student.id

    db.session.commit()

    return jsonify(user.to_dict()), 200