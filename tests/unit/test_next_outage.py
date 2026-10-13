from datetime import datetime

from app.services.parser import parse_intervals
from app.services.status import minutes_until, next_outage

SCHEDULE = parse_intervals("08:00-12:00, 16:00-20:00")


def test_next_outage_later_today_when_power_is_on():
    now = datetime(2026, 10, 13, 13, 0)
    outage = next_outage(SCHEDULE, now)
    assert outage == datetime(2026, 10, 13, 16, 0)
    assert minutes_until(outage, now) == 180


def test_next_outage_during_outage_is_the_following_one():
    assert next_outage(SCHEDULE, datetime(2026, 10, 13, 10, 0)) == datetime(2026, 10, 13, 16, 0)


def test_next_outage_tomorrow():
    now = datetime(2026, 10, 13, 21, 0)
    outage = next_outage(SCHEDULE, now)
    assert outage == datetime(2026, 10, 14, 8, 0)
    assert minutes_until(outage, now) == 660


def test_no_outages_returns_none():
    now = datetime(2026, 10, 13, 13, 0)
    assert next_outage([], now) is None
    assert minutes_until(None, now) is None
