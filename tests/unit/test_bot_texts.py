from datetime import datetime

import pytest

from app.seed import seed_addresses, seed_schedule
from bot.texts import address_text, parse_address, status_text


@pytest.fixture
def seeded(session):
    seed_addresses(session)
    seed_schedule(session)
    return session


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Шевченка 10", ("Шевченка", "10")),
        ("Княгині Ольги, 14", ("Княгині Ольги", "14")),
        ("10", None),
    ],
)
def test_parse_address(text, expected):
    assert parse_address(text) == expected


def test_address_text(seeded):
    assert address_text(seeded, "Шевченка", "10") == "Шевченка, 10 — черга 2"
    assert "не знайдено" in address_text(seeded, "Нема", "1")


def test_status_text_uses_same_services_as_api(seeded):
    text = status_text(seeded, "Шевченка", "10", datetime(2026, 10, 13, 13, 0))
    assert "черга 2" in text
    assert "Світла немає" in text
    assert "Увімкнення о 16:00" in text
