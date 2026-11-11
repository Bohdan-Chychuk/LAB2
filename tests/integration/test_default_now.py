"""SVL-34: без параметра now API бере київський час, а не локальний час сервера."""

from datetime import datetime

import app.clock


def test_status_without_now_uses_kyiv_clock(client, monkeypatch):
    monkeypatch.setattr(app.clock, "now_local", lambda: datetime(2026, 10, 13, 13, 0))
    client.post("/schedules/import", json={"queues": {"2": "12:00-16:00"}})

    body = client.get("/status", params={"street": "Шевченка", "house": "10"}).json()

    assert body["now"] == "2026-10-13T13:00:00"
    assert body["planned"] == "off"


def test_aware_now_parameter_is_converted_to_kyiv_time(client):
    client.post("/schedules/import", json={"queues": {"2": "12:00-16:00"}})
    params = {"street": "Шевченка", "house": "10", "now": "2026-10-13T10:00:00+00:00"}

    body = client.get("/status", params=params).json()

    assert body["now"] == "2026-10-13T13:00:00"
    assert body["planned"] == "off"
