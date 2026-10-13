def test_get_queue_for_known_address(client):
    response = client.get("/queue", params={"street": "Шевченка", "house": "10"})
    assert response.status_code == 200
    assert response.json() == {"street": "Шевченка", "house": "10", "queue": 2}


def test_get_queue_for_unknown_address_returns_404(client):
    response = client.get("/queue", params={"street": "Шевченка", "house": "999"})
    assert response.status_code == 404
    assert "не знайдено" in response.json()["detail"]
