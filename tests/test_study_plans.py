import pytest
from app import create_app
from app.extensions import db
from app.models.group import Group
from app.models.discipline import Discipline


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
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
        g = Group(group_name="241-352", year=3)
        d = Discipline(discipline_name="DevOps")
        db.session.add_all([g, d])
        db.session.commit()
        return {"group_id": g.id, "discipline_id": d.id}


def test_create_study_plan(client, seed):
    response = client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    assert response.status_code == 201


def test_create_study_plan_bad_semester(client, seed):
    response = client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 0,
    })
    assert response.status_code == 400


def test_create_study_plan_no_group(client, seed):
    response = client.post("/study_plans", json={
        "group_id": 99999,
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    assert response.status_code == 400