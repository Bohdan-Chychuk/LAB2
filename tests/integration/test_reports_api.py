ADDRESS = {"street": "Шевченка", "house": "10"}


def report(client, user_id, status="off", now="2026-10-13T18:00:00", **address):
    payload = {"user_id": user_id, "status": status, **(address or ADDRESS)}
    return client.post("/reports", json=payload, params={"now": now})


def test_post_report_returns_201(client):
    response = report(client, "u1")
    assert response.status_code == 201
    assert response.json()["status"] == "off"
    assert response.json()["created_at"] == "2026-10-13T18:00:00"


def test_post_report_unknown_address_404(client):
    assert report(client, "u1", street="Нема", house="1").status_code == 404


def test_post_report_invalid_status_422(client):
    assert report(client, "u1", status="maybe").status_code == 422
