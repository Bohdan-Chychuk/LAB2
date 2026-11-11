import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[2] / "data" / "schedules"


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_import_then_reimport_changed_schedule(client):
    first = client.post("/schedules/import", json=_load("today.json"))
    assert first.status_code == 200
    assert first.json() == {"changed_queues": [1, 2, 3, 4, 5, 6]}

    same = client.post("/schedules/import", json=_load("today.json"))
    assert same.json() == {"changed_queues": []}

    changed = client.post("/schedules/import", json=_load("changed.json"))
    assert changed.json() == {"changed_queues": [3]}


def test_import_invalid_schedule_returns_422(client):
    response = client.post("/schedules/import", json={"queues": {"1": "вранці"}})
    assert response.status_code == 422


def test_get_schedule_for_queue(client):
    client.post("/schedules/import", json=_load("today.json"))
    response = client.get("/schedule/1")
    assert response.status_code == 200
    assert response.json() == {
        "queue": 1,
        "intervals": [{"start": "08:00", "end": "12:00"}, {"start": "16:00", "end": "20:00"}],
    }
    assert client.get("/schedule/42").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"queues": {"1": 5}},  # число замість рядка
        {"queues": {"1": None}},
        {"queues": {"0": "08:00-12:00"}},  # черги нумеруються з 1
        {"queues": {"перша": "08:00-12:00"}},
        {"queue": {"1": "08:00-12:00"}},  # помилка в назві поля
    ],
)
def test_import_malformed_schedule_returns_422_not_500(client, payload):
    response = client.post("/schedules/import", json=payload)
    assert response.status_code == 422
    assert client.get("/schedule/1").status_code == 404  # нічого не збережено


def test_schedule_import_schema_is_documented(client):
    schema = client.get("/openapi.json").json()
    body = schema["paths"]["/schedules/import"]["post"]["requestBody"]
    assert body["content"]["application/json"]["schema"]["$ref"].endswith("/ScheduleIn")
