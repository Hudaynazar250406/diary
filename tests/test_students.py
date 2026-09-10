def test_create_student_success(client):
    group_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = group_resp.get_json()["id"]

    response = client.post(
        "/students",
        json={"full_name": "Мерданов Худайназар", "group_id": group_id},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["full_name"] == "Мерданов Худайназар"


def test_create_student_missing_full_name(client):
    group_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = group_resp.get_json()["id"]

    response = client.post("/students", json={"group_id": group_id})
    assert response.status_code == 400


def test_create_student_nonexistent_group(client):
    response = client.post(
        "/students", json={"full_name": "Тест Тестович", "group_id": 999}
    )
    assert response.status_code == 400


def test_get_student_not_found(client):
    response = client.get("/students/999")
    assert response.status_code == 404


def test_update_student_success(client):
    group_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = group_resp.get_json()["id"]
    create_resp = client.post(
        "/students", json={"full_name": "Тест Тестович", "group_id": group_id}
    )
    student_id = create_resp.get_json()["id"]

    response = client.put(
        f"/students/{student_id}", json={"full_name": "Новое Имя"}
    )
    assert response.status_code == 200
    assert response.get_json()["full_name"] == "Новое Имя"


def test_update_student_not_found(client):
    response = client.put("/students/999", json={"full_name": "Новое Имя"})
    assert response.status_code == 404


def test_update_student_nonexistent_group(client):
    group_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = group_resp.get_json()["id"]
    create_resp = client.post(
        "/students", json={"full_name": "Тест Тестович", "group_id": group_id}
    )
    student_id = create_resp.get_json()["id"]

    response = client.put(f"/students/{student_id}", json={"group_id": 999})
    assert response.status_code == 400


def test_delete_student_success(client):
    group_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = group_resp.get_json()["id"]
    create_resp = client.post(
        "/students", json={"full_name": "Тест Тестович", "group_id": group_id}
    )
    student_id = create_resp.get_json()["id"]

    response = client.delete(f"/students/{student_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/students/{student_id}")
    assert get_resp.status_code == 404


def test_delete_student_not_found(client):
    response = client.delete("/students/999")
    assert response.status_code == 404
