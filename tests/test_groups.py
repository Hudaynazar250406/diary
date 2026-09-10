def test_create_group_success(client):
    response = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    assert response.status_code == 201
    body = response.get_json()
    assert body["group_name"] == "241-352"


def test_create_group_missing_group_name(client):
    response = client.post("/groups", json={"year": 2024})
    assert response.status_code == 400


def test_create_group_missing_body(client):
    response = client.post("/groups")
    assert response.status_code == 400


def test_list_groups_empty(client):
    response = client.get("/groups")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_group_not_found(client):
    response = client.get("/groups/999")
    assert response.status_code == 404


def test_update_group_success(client):
    create_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = create_resp.get_json()["id"]

    response = client.put(f"/groups/{group_id}", json={"group_name": "241-353"})
    assert response.status_code == 200
    assert response.get_json()["group_name"] == "241-353"


def test_update_group_not_found(client):
    response = client.put("/groups/999", json={"group_name": "241-353"})
    assert response.status_code == 404


def test_delete_group_success(client):
    create_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = create_resp.get_json()["id"]

    response = client.delete(f"/groups/{group_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/groups/{group_id}")
    assert get_resp.status_code == 404


def test_delete_group_not_found(client):
    response = client.delete("/groups/999")
    assert response.status_code == 404


def test_delete_group_with_students_fails(client):
    group_resp = client.post("/groups", json={"group_name": "241-352", "year": 2024})
    group_id = group_resp.get_json()["id"]

    client.post("/students", json={"full_name": "Тест Тестович", "group_id": group_id})

    response = client.delete(f"/groups/{group_id}")
    assert response.status_code == 400
