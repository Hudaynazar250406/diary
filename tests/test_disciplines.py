import pytest
from app import create_app
from app.extensions import db


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


def test_create_discipline(client):
    """Создание дисциплины с корректными данными."""
    response = client.post("/disciplines", json={"discipline_name": "DevOps"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["discipline_name"] == "DevOps"
    assert "id" in data


def test_create_discipline_missing_field(client):
    """Создание без обязательного поля discipline_name."""
    response = client.post("/disciplines", json={})
    assert response.status_code == 400


def test_create_discipline_empty_name(client):
    """Создание с пустым названием."""
    response = client.post("/disciplines", json={"discipline_name": ""})
    assert response.status_code == 400


def test_get_disciplines(client):
    """Получение списка всех дисциплин."""
    client.post("/disciplines", json={"discipline_name": "Math"})
    client.post("/disciplines", json={"discipline_name": "Physics"})
    response = client.get("/disciplines")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_discipline_by_id(client):
    """Получение дисциплины по ID."""
    create_resp = client.post("/disciplines", json={"discipline_name": "History"})
    discipline_id = create_resp.get_json()["id"]
    response = client.get(f"/disciplines/{discipline_id}")
    assert response.status_code == 200
    assert response.get_json()["discipline_name"] == "History"


def test_get_nonexistent_discipline(client):
    """Запрос несуществующей дисциплины."""
    response = client.get("/disciplines/99999")
    assert response.status_code == 404


def test_update_discipline(client):
    """Обновление существующей дисциплины."""
    create_resp = client.post("/disciplines", json={"discipline_name": "Old"})
    discipline_id = create_resp.get_json()["id"]
    response = client.put(f"/disciplines/{discipline_id}", json={"discipline_name": "New"})
    assert response.status_code == 200
    assert response.get_json()["discipline_name"] == "New"


def test_delete_discipline(client):
    """Удаление дисциплины."""
    create_resp = client.post("/disciplines", json={"discipline_name": "ToDelete"})
    discipline_id = create_resp.get_json()["id"]
    response = client.delete(f"/disciplines/{discipline_id}")
    assert response.status_code == 200
    # Проверяем, что её больше нет
    response = client.get(f"/disciplines/{discipline_id}")
    assert response.status_code == 404