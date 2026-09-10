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
