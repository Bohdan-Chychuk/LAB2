"""SVL-26: імпорт графіка через API → GET /status повертає очікуваний стан (TestClient + SQLite)."""

import json
from pathlib import Path

from app.main import create_app

DATA = Path(__file__).resolve().parents[2] / "data" / "schedules"
ADDRESS = {"street": "Шевченка", "house": "25"}  # черга 3


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def status_at(client, iso: str) -> dict:
    return client.get("/status", params={**ADDRESS, "now": iso}).json()


def test_import_then_status_then_changed_schedule(client):
    assert client.get("/queue", params=ADDRESS).json()["queue"] == 3

    client.post("/schedules/import", json=_load("today.json"))  # черга 3: 04:00-08:00, 20:00-24:00
    body = status_at(client, "2026-10-13T09:00:00")
    assert body["planned"] == "on"
    assert body["next_outage"] == "2026-10-13T20:00:00"

    changed = client.post("/schedules/import", json=_load("changed.json")).json()
    assert changed["changed_queues"] == [3]  # черга 3: 06:00-10:00, 20:00-24:00

    body = status_at(client, "2026-10-13T09:00:00")
    assert body["planned"] == "off"
    assert body["next_change"] == "2026-10-13T10:00:00"


def test_data_persists_between_app_instances(db_url):
    from fastapi.testclient import TestClient

    with TestClient(create_app(db_url, demo_schedule=False)) as client:
        client.post("/schedules/import", json=_load("today.json"))
    with TestClient(create_app(db_url)) as client:
        assert status_at(client, "2026-10-13T05:00:00")["planned"] == "off"
