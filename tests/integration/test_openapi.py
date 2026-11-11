"""SVL-39: кожна відповідь API описана схемою — Swagger показує формат, а не порожній object."""

import pytest

ENDPOINTS = [
    ("/queue", "get", "QueueOut"),
    ("/status", "get", "StatusOut"),
    ("/schedule/{queue}", "get", "ScheduleOut"),
    ("/schedules/import", "post", "ChangedQueuesOut"),
    ("/subscriptions", "post", "SubscriptionOut"),
    ("/reports", "post", "ReportOut"),
]


@pytest.fixture(scope="module")
def openapi():
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app("sqlite://", demo_schedule=False)) as client:
        return client.get("/openapi.json").json()


@pytest.mark.parametrize(("path", "method", "model"), ENDPOINTS)
def test_response_has_named_schema(openapi, path, method, model):
    responses = openapi["paths"][path][method]["responses"]
    success = responses.get("200") or responses["201"]
    assert success["content"]["application/json"]["schema"]["$ref"].endswith(f"/{model}")


def test_status_schema_lists_fields(openapi):
    fields = openapi["components"]["schemas"]["StatusOut"]["properties"]
    assert {"planned", "next_change", "next_outage", "minutes_to_outage", "actual"} <= set(fields)
