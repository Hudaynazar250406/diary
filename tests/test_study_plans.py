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
    """Создаёт тестовые группу и дисциплину."""
    with app.app_context():
        g = Group(group_name="241-352", year=3)
        d = Discipline(discipline_name="DevOps")
        db.session.add_all([g, d])
        db.session.commit()
        return {"group_id": g.id, "discipline_id": d.id}


def test_create_study_plan(client, seed):
    """Создание учебного плана с корректными данными."""
    response = client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["semester"] == 1
    assert data["group_id"] == seed["group_id"]
    assert data["discipline_id"] == seed["discipline_id"]


def test_get_study_plans(client, seed):
    """Получение списка всех учебных планов."""
    client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 2,
    })
    response = client.get("/study_plans")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_update_study_plan(client, seed):
    """Обновление существующего учебного плана."""
    create_resp = client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    plan_id = create_resp.get_json()["id"]

    response = client.put(f"/study_plans/{plan_id}", json={"semester": 3})
    assert response.status_code == 200
    assert response.get_json()["semester"] == 3


def test_delete_study_plan(client, seed):
    """Удаление учебного плана."""
    create_resp = client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    plan_id = create_resp.get_json()["id"]

    response = client.delete(f"/study_plans/{plan_id}")
    assert response.status_code == 200

    # Проверяем, что план больше не существует
    response = client.get(f"/study_plans/{plan_id}")
    assert response.status_code == 404


def test_create_study_plan_nonexistent_group(client, seed):
    """Попытка создания плана с несуществующей группой."""
    response = client.post("/study_plans", json={
        "group_id": 99999,
        "discipline_id": seed["discipline_id"],
        "semester": 1,
    })
    assert response.status_code == 400


def test_create_study_plan_nonexistent_discipline(client, seed):
    """Попытка создания плана с несуществующей дисциплиной."""
    response = client.post("/study_plans", json={
        "group_id": seed["group_id"],
        "discipline_id": 99999,
        "semester": 1,
    })
    assert response.status_code == 400


def test_create_study_plan_missing_fields(client):
    """Попытка создания плана без обязательных полей."""
    response = client.post("/study_plans", json={})
    assert response.status_code == 400