import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[2] / "data" / "schedules"


@pytest.fixture
def imported(client):
    data = json.loads((DATA / "today.json").read_text(encoding="utf-8"))
    client.post("/schedules/import", json=data)
    return client


def subscribe(client, user_id, notify_before=30, quiet_hours=False):
    return client.post(
        "/subscriptions",
        json={
            "user_id": user_id,
            "street": "Шевченка",
            "house": "10",  # черга 2: 00:00-04:00, 12:00-16:00
            "notify_before": notify_before,
            "quiet_hours": quiet_hours,
        },
    )


def test_create_subscription(imported):
    response = subscribe(imported, "alice")
    assert response.status_code == 201
    assert response.json()["queue"] == 2


def test_subscription_rejects_unsupported_lead_time(imported):
    assert subscribe(imported, "alice", notify_before=20).status_code == 422


def test_due_notifications_in_window(imported):
    subscribe(imported, "alice", notify_before=30)
    subscribe(imported, "bob", notify_before=60)
    due = imported.get("/notifications/due", params={"now": "2026-10-13T11:31:00"}).json()
    assert [n["user_id"] for n in due] == ["alice"]
    assert due[0]["outage_start"] == "2026-10-13T12:00:00"


def test_no_due_notifications_outside_window(imported):
    subscribe(imported, "alice", notify_before=30)
    assert imported.get("/notifications/due", params={"now": "2026-10-13T11:20:00"}).json() == []
