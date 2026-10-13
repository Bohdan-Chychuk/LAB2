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


def test_three_reports_set_actual_status(client):
    for user, house in (("u1", "10"), ("u2", "25"), ("u3", "48")):
        assert report(client, user, house=house, street="Шевченка").status_code == 201
    params = {**ADDRESS, "now": "2026-10-13T18:05:00"}
    assert client.get("/status", params=params).json()["actual"] == "off"


def test_actual_is_null_without_enough_reports(client):
    report(client, "u1")
    params = {**ADDRESS, "now": "2026-10-13T18:05:00"}
    assert client.get("/status", params=params).json()["actual"] is None


def test_repeated_report_within_10_minutes_returns_429(client):
    assert report(client, "u1", now="2026-10-13T18:00:00").status_code == 201
    response = report(client, "u1", status="on", now="2026-10-13T18:05:00")
    assert response.status_code == 429
    assert report(client, "u1", status="on", now="2026-10-13T18:10:00").status_code == 201
