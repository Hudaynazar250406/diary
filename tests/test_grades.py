import pytest

from app import create_app
from app.extensions import db
from app.models.group import Group
from app.models.student import Student
from app.models.discipline import Discipline
from app.models.study_plan import StudyPlan


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed(app):
    with app.app_context():
        group = Group(
            group_name="241-352",
            year=3,
        )

        discipline = Discipline(
            discipline_name="DevOps",
        )

        other_discipline = Discipline(
            discipline_name="Криптография",
        )

        db.session.add_all([group, discipline, other_discipline])
        db.session.flush()

        student = Student(
            full_name="Иван Иванов",
            group_id=group.id,
        )

        study_plan = StudyPlan(
            group_id=group.id,
            discipline_id=discipline.id,
            semester=1,
        )

        db.session.add_all([student, study_plan])
        db.session.commit()

        return {
            "student_id": student.id,
            "discipline_id": discipline.id,
            "other_discipline_id": other_discipline.id,
        }


def test_create_grade_one(client, seed):
    response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": 1,
    })

    assert response.status_code == 201

    data = response.get_json()

    assert data["grade"] == 1
    assert data["student_id"] == seed["student_id"]
    assert data["discipline_id"] == seed["discipline_id"]
    assert data["date"]


def test_create_grade_five(client, seed):
    response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": 5,
    })

    assert response.status_code == 201
    assert response.get_json()["grade"] == 5


@pytest.mark.parametrize("value", [0, 6])
def test_create_invalid_grade(client, seed, value):
    response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": value,
    })

    assert response.status_code == 400


def test_create_grade_nonexistent_student(client, seed):
    response = client.post("/grades", json={
        "student_id": 99999,
        "discipline_id": seed["discipline_id"],
        "grade": 5,
    })

    assert response.status_code == 404


def test_create_grade_nonexistent_discipline(client, seed):
    response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": 99999,
        "grade": 5,
    })

    assert response.status_code == 404


def test_create_grade_outside_study_plan(client, seed):
    response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["other_discipline_id"],
        "grade": 5,
    })

    assert response.status_code == 400


def test_get_grades(client, seed):
    client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": 4,
    })

    response = client.get("/grades")

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_grade_by_id(client, seed):
    create_response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": 4,
    })

    grade_id = create_response.get_json()["id"]

    response = client.get(f"/grades/{grade_id}")

    assert response.status_code == 200
    assert response.get_json()["grade"] == 4


def test_update_grade(client, seed):
    create_response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": 3,
    })

    grade_id = create_response.get_json()["id"]

    response = client.put(f"/grades/{grade_id}", json={
        "grade": 5,
    })

    assert response.status_code == 200
    assert response.get_json()["grade"] == 5


def test_delete_grade(client, seed):
    create_response = client.post("/grades", json={
        "student_id": seed["student_id"],
        "discipline_id": seed["discipline_id"],
        "grade": 4,
    })

    grade_id = create_response.get_json()["id"]

    response = client.delete(f"/grades/{grade_id}")

    assert response.status_code == 200

    response = client.get(f"/grades/{grade_id}")

    assert response.status_code == 404
