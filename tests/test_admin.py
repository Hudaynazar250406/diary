from app.extensions import db
from app.models.group import Group
from app.models.student import Student
from app.models.user import User


def create_user(
    app,
    username,
    role=User.ROLE_STUDENT,
    student_id=None,
):
    with app.app_context():
        user = User(
            username=username,
            email=f"{username}@example.com",
            role=role,
            student_id=student_id,
        )

        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        return user.id


def test_admin_can_list_users(
    client,
    app,
):
    create_user(
        app,
        "student_one",
    )

    response = client.get(
        "/admin/users",
    )

    assert response.status_code == 200

    users = response.get_json()

    assert len(users) == 2


def test_admin_can_assign_teacher_role(
    client,
    app,
):
    user_id = create_user(
        app,
        "future_teacher",
    )

    response = client.put(
        f"/admin/users/{user_id}/role",
        json={
            "role": User.ROLE_TEACHER,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["role"] == User.ROLE_TEACHER

    with app.app_context():
        user = db.session.get(
            User,
            user_id,
        )

        assert user.role == User.ROLE_TEACHER


def test_admin_cannot_assign_admin_role_from_api(
    client,
    app,
):
    user_id = create_user(
        app,
        "normal_user",
    )

    response = client.put(
        f"/admin/users/{user_id}/role",
        json={
            "role": User.ROLE_ADMIN,
        },
    )

    assert response.status_code == 400


def test_admin_cannot_change_admin_role_from_api(
    client,
    app,
):
    with app.app_context():
        admin = User.query.filter_by(
            role=User.ROLE_ADMIN,
        ).first()

        admin_id = admin.id

    response = client.put(
        f"/admin/users/{admin_id}/role",
        json={
            "role": User.ROLE_STUDENT,
        },
    )

    assert response.status_code == 400


def test_admin_cannot_update_nonexistent_user(
    client,
):
    response = client.put(
        "/admin/users/99999/role",
        json={
            "role": User.ROLE_TEACHER,
        },
    )

    assert response.status_code == 404


def test_admin_can_link_user_to_student(
    client,
    app,
):
    with app.app_context():
        group = Group(
            group_name="241-352",
            year=2026,
        )

        db.session.add(group)
        db.session.flush()

        student = Student(
            full_name="Иван Иванов",
            group_id=group.id,
        )

        db.session.add(student)
        db.session.commit()

        student_id = student.id

    user_id = create_user(
        app,
        "ivan",
    )

    response = client.put(
        f"/admin/users/{user_id}/student",
        json={
            "student_id": student_id,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["student_id"] == student_id


def test_teacher_cannot_be_linked_to_student(
    client,
    app,
):
    user_id = create_user(
        app,
        "teacher_user",
        role=User.ROLE_TEACHER,
    )

    response = client.put(
        f"/admin/users/{user_id}/student",
        json={
            "student_id": 1,
        },
    )

    assert response.status_code == 400


def test_student_can_be_unlinked(
    client,
    app,
):
    with app.app_context():
        group = Group(
            group_name="241-353",
            year=2026,
        )

        db.session.add(group)
        db.session.flush()

        student = Student(
            full_name="Пётр Петров",
            group_id=group.id,
        )

        db.session.add(student)
        db.session.commit()

        student_id = student.id

    user_id = create_user(
        app,
        "petr",
        student_id=student_id,
    )

    response = client.put(
        f"/admin/users/{user_id}/student",
        json={
            "student_id": None,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["student_id"] is None


def test_student_cannot_be_linked_twice(
    client,
    app,
):
    with app.app_context():
        group = Group(
            group_name="241-354",
            year=2026,
        )

        db.session.add(group)
        db.session.flush()

        student = Student(
            full_name="Существующий студент",
            group_id=group.id,
        )

        db.session.add(student)
        db.session.commit()

        student_id = student.id

    create_user(
        app,
        "first_user",
        student_id=student_id,
    )

    second_user_id = create_user(
        app,
        "second_user",
    )

    response = client.put(
        f"/admin/users/{second_user_id}/student",
        json={
            "student_id": student_id,
        },
    )

    assert response.status_code == 400