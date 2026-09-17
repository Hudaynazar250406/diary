def test_create_discipline(client):
    """Создание дисциплины с корректными данными."""
    response = client.post(
        "/disciplines",
        json={"discipline_name": "DevOps"},
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["discipline_name"] == "DevOps"
    assert "id" in data


def test_create_discipline_missing_field(client):
    """Создание без обязательного поля discipline_name."""
    response = client.post(
        "/disciplines",
        json={},
    )

    assert response.status_code == 400


def test_create_discipline_empty_name(client):
    """Создание с пустым названием."""
    response = client.post(
        "/disciplines",
        json={"discipline_name": ""},
    )

    assert response.status_code == 400


def test_get_disciplines(client):
    """Получение списка всех дисциплин."""
    client.post(
        "/disciplines",
        json={"discipline_name": "Math"},
    )

    client.post(
        "/disciplines",
        json={"discipline_name": "Physics"},
    )

    response = client.get("/disciplines")

    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_discipline_by_id(client):
    """Получение дисциплины по ID."""
    create_response = client.post(
        "/disciplines",
        json={"discipline_name": "History"},
    )

    discipline_id = create_response.get_json()["id"]

    response = client.get(
        f"/disciplines/{discipline_id}",
    )

    assert response.status_code == 200
    assert (
        response.get_json()["discipline_name"]
        == "History"
    )


def test_get_nonexistent_discipline(client):
    """Запрос несуществующей дисциплины."""
    response = client.get(
        "/disciplines/99999",
    )

    assert response.status_code == 404


def test_update_discipline(client):
    """Обновление существующей дисциплины."""
    create_response = client.post(
        "/disciplines",
        json={"discipline_name": "Old"},
    )

    discipline_id = create_response.get_json()["id"]

    response = client.put(
        f"/disciplines/{discipline_id}",
        json={"discipline_name": "New"},
    )

    assert response.status_code == 200
    assert (
        response.get_json()["discipline_name"]
        == "New"
    )


def test_delete_discipline(client):
    """Удаление дисциплины."""
    create_response = client.post(
        "/disciplines",
        json={"discipline_name": "ToDelete"},
    )

    discipline_id = create_response.get_json()["id"]

    response = client.delete(
        f"/disciplines/{discipline_id}",
    )

    assert response.status_code == 200

    response = client.get(
        f"/disciplines/{discipline_id}",
    )

    assert response.status_code == 404