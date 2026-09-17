import datetime

import pytest

from app.extensions import db
from app.models.discipline import Discipline
from app.models.grade import Grade
from app.models.group import Group
from app.models.schedule import Schedule
from app.models.student import Student
from app.models.study_plan import StudyPlan
from app.models.user import User


@pytest.fixture
def student_portal(app):
    with app.app_context():
        group = Group(
            group_name="241-352",
            year=2026,
        )

        other_group = Group(
            group_name="241-353",
            year=2026,
        )

        devops = Discipline(
            discipline_name="DevOps",
        )

        cryptography = Discipline(
            discipline_name="Криптография",
        )

        db.session.add_all(
            [
                group,
                other_group,
                devops,
                cryptography,
            ]
        )

        db.session.flush()

        student = Student(
            full_name="Иван Иванов",
            group_id=group.id,
        )

        other_student = Student(
            full_name="Пётр Петров",
            group_id=other_group.id,
        )

        db.session.add_all(
            [
                student,
                other_student,
            ]
        )

        db.session.flush()

        db.session.add_all(
            [
                StudyPlan(
                    group_id=group.id,
                    discipline_id=devops.id,
                    semester=1,
                ),
                StudyPlan(
                    group_id=group.id,
                    discipline_id=cryptography.id,
                    semester=2,
                ),
            ]
        )

        db.session.add_all(
            [
                Grade(
                    student_id=student.id,
                    discipline_id=devops.id,
                    grade=5,
                ),
                Grade(
                    student_id=other_student.id,
                    discipline_id=devops.id,
                    grade=2,
                ),
            ]
        )

        db.session.add_all(
            [
                Schedule(
                    group_id=group.id,
                    discipline_id=devops.id,
                    weekday=1,
                    start_time=datetime.time(9, 0),
                    end_time=datetime.time(10, 30),
                    room="401",
                ),
                Schedule(
                    group_id=group.id,
                    discipline_id=cryptography.id,
                    weekday=3,
                    start_time=datetime.time(11, 0),
                    end_time=datetime.time(12, 30),
                    room="402",
                ),
                Schedule(
                    group_id=other_group.id,
                    discipline_id=devops.id,
                    weekday=2,
                    start_time=datetime.time(9, 0),
                    end_time=datetime.time(10, 30),
                    room="500",
                ),
            ]
        )

        user = User(
            username="linked_student",
            email="linked_student@example.com",
            role=User.ROLE_STUDENT,
            student_id=student.id,
        )

        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        user_id = user.id

    test_client = app.test_client()

    with test_client.session_transaction() as session:
        session["user_id"] = user_id

    return test_client


def test_unlinked_student_cannot_get_personal_data(
    student_client,
):
    response = student_client.get(
        "/me/grades",
    )

    assert response.status_code == 400


def test_student_sees_only_own_grades(
    student_portal,
):
    response = student_portal.get(
        "/me/grades",
    )

    assert response.status_code == 200

    grades = response.get_json()

    assert len(grades) == 1
    assert grades[0]["grade"] == 5
    assert grades[0]["discipline_name"] == "DevOps"


def test_student_sees_own_disciplines(
    student_portal,
):
    response = student_portal.get(
        "/me/disciplines",
    )

    assert response.status_code == 200

    disciplines = response.get_json()

    assert len(disciplines) == 2

    names = {
        discipline["discipline_name"]
        for discipline in disciplines
    }

    assert names == {
        "DevOps",
        "Криптография",
    }


def test_student_sees_only_group_schedule(
    student_portal,
):
    response = student_portal.get(
        "/me/schedule",
    )

    assert response.status_code == 200

    schedule = response.get_json()

    assert len(schedule) == 2

    assert schedule[0]["weekday_name"] == "Понедельник"
    assert schedule[0]["discipline_name"] == "DevOps"

    assert schedule[1]["weekday_name"] == "Среда"
    assert schedule[1]["discipline_name"] == "Криптография"


def test_teacher_cannot_use_student_personal_endpoint(
    teacher_client,
):
    response = teacher_client.get(
        "/me/grades",
    )

    assert response.status_code == 403