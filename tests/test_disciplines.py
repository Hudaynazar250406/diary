import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()

def test_create_discipline(client):
    response = client.post("/disciplines", json={"discipline_name": "DevOps"})
    assert response.status_code == 201
    assert response.get_json()["discipline_name"] == "DevOps"

def test_create_discipline_empty_name(client):
    response = client.post("/disciplines", json={"discipline_name": ""})
    assert response.status_code == 400

def test_get_disciplines(client):
    client.post("/disciplines", json={"discipline_name": "Math"})
    response = client.get("/disciplines")
    assert response.status_code == 200