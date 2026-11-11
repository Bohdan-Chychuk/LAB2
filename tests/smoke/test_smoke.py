"""Smoke-тести розгорнутого застосунку — стадія CD «Deploy → staging».

Запуск: BASE_URL=http://127.0.0.1:8000 pytest tests/smoke -v
Без BASE_URL тести пропускаються, тому не заважають звичайному прогону pytest.
"""

import os

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL")

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(not BASE_URL, reason="BASE_URL не задано — немає розгорнутого середовища"),
]


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        yield client


def test_health(api):
    assert api.get("/health").json() == {"status": "ok"}


def test_web_page_and_static_assets(api):
    page = api.get("/")
    assert page.status_code == 200
    assert "СвітлоЛьвів" in page.text
    assert api.get("/static/app.js").status_code == 200
    assert api.get("/static/style.css").status_code == 200


def test_seeded_address_has_queue(api):
    body = api.get("/queue", params={"street": "Шевченка", "house": "10"}).json()
    assert body["queue"] == 2


def test_demo_schedule_and_status(api):
    assert api.get("/schedule/1").json()["intervals"]
    status = api.get("/status", params={"street": "Шевченка", "house": "10"}).json()
    assert status["planned"] in {"on", "off"}


def test_openapi_is_published(api):
    assert "/status" in api.get("/openapi.json").json()["paths"]
