import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[2] / "data" / "schedules"
ADDRESS = {"street": "Шевченка", "house": "10"}  # черга 2: 00:00-04:00, 12:00-16:00


@pytest.fixture
def imported(client):
    data = json.loads((DATA / "today.json").read_text(encoding="utf-8"))
    client.post("/schedules/import", json=data)
    return client


def test_status_during_outage(imported):
    body = imported.get("/status", params={**ADDRESS, "now": "2026-10-13T13:00:00"}).json()
    assert body["queue"] == 2
    assert body["planned"] == "off"
    assert body["next_change"] == "2026-10-13T16:00:00"


def test_status_when_power_is_on(imported):
    body = imported.get("/status", params={**ADDRESS, "now": "2026-10-13T10:00:00"}).json()
    assert body["planned"] == "on"
    assert body["next_change"] == "2026-10-13T12:00:00"


def test_status_unknown_address_404(imported):
    assert imported.get("/status", params={"street": "Нема", "house": "1"}).status_code == 404
