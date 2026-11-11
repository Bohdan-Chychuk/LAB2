"""SVL-45: дані з сервера не вставляються як HTML (захист від XSS через innerHTML)."""

import json

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e

PAYLOAD = '<img src=x onerror="window.__xss = true">'


def test_street_suggestions_are_not_rendered_as_html(page: Page, live_server):
    page.route("**/streets?*", lambda route: route.fulfill(json=[PAYLOAD]))
    page.goto(live_server)
    page.fill("#street", "Ше")
    page.wait_for_function("document.querySelectorAll('#streets option').length > 0")
    assert page.evaluate("window.__xss") is None
    assert page.locator("#streets option").first.get_attribute("value") == PAYLOAD


def test_schedule_is_not_rendered_as_html(page: Page, live_server):
    body = {"queue": 2, "intervals": [{"start": PAYLOAD, "end": "12:00"}]}
    page.route("**/schedule/*", lambda route: route.fulfill(body=json.dumps(body)))
    page.goto(live_server)
    page.fill("#street", "Шевченка")
    page.fill("#house", "10")
    page.click("#find")
    expect(page.locator("#schedule")).to_contain_text("<img")
    assert page.evaluate("window.__xss") is None
