"""SVL-27: відкрити /, ввести адресу, побачити графік, тричі «Світла немає» → фактичний стан off."""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


def open_address(page: Page, url: str, street: str, house: str) -> None:
    page.goto(url)
    page.fill("#street", street)
    page.fill("#house", house)
    page.click("#find")
    expect(page.locator("#result")).to_be_visible()


def test_address_shows_queue_and_schedule(page: Page, live_server):
    open_address(page, live_server, "Шевченка", "10")
    expect(page.locator("#queue")).to_have_text("2")
    expect(page.locator("#schedule")).to_contain_text("12:00")
    expect(page.locator("#schedule")).to_contain_text("16:00")
    expect(page.locator("#status-indicator")).to_have_text(re.compile("Світло є|Світла немає"))


def test_unknown_address_shows_error(page: Page, live_server):
    page.goto(live_server)
    page.fill("#street", "Неіснуюча")
    page.fill("#house", "1")
    page.click("#find")
    expect(page.locator("#error")).to_contain_text("не знайдено")


def test_three_reports_switch_actual_status_to_off(page: Page, live_server):
    open_address(page, live_server, "Городоцька", "120")
    expect(page.locator("#actual")).to_contain_text("недостатньо репортів")

    for user_id in ("e2e-user-1", "e2e-user-2", "e2e-user-3"):
        page.fill("#user-id", user_id)
        page.click("#btn-off")
        expect(page.locator("#report-message")).to_contain_text(user_id)

    expect(page.locator("#actual")).to_contain_text("світла немає")


def test_mobile_layout_has_no_horizontal_scroll(page: Page, live_server):
    page.set_viewport_size({"width": 375, "height": 740})
    open_address(page, live_server, "Шевченка", "10")
    overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
    assert overflow is False
