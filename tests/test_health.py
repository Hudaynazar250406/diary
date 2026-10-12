def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "ok"


def test_health_includes_instance_id(client):
    response = client.get("/health")
    data = response.get_json()
    assert isinstance(data["instance"], str)
    assert len(data["instance"]) > 0
