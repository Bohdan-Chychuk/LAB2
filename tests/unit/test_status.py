from datetime import datetime

from app.services.parser import parse_intervals
from app.services.status import is_power_on, next_change

DAY = datetime(2026, 10, 13)
SCHEDULE = parse_intervals("08:00-12:00, 16:00-20:00")


def at(hour: int, minute: int = 0, day_offset: int = 0) -> datetime:
    return DAY.replace(day=DAY.day + day_offset, hour=hour, minute=minute)


def test_power_off_during_outage_and_next_change_is_its_end():
    assert is_power_on(SCHEDULE, at(10)) is False
    assert next_change(SCHEDULE, at(10)) == at(12)


def test_power_on_between_outages_and_next_change_is_next_start():
    assert is_power_on(SCHEDULE, at(13)) is True
    assert next_change(SCHEDULE, at(13)) == at(16)


def test_interval_start_inclusive_end_exclusive():
    assert is_power_on(SCHEDULE, at(8)) is False
    assert is_power_on(SCHEDULE, at(12)) is True


def test_after_last_outage_next_change_is_tomorrow():
    assert next_change(SCHEDULE, at(21)) == at(8, day_offset=1)


def test_outage_crossing_midnight():
    schedule = parse_intervals("22:00-02:00")
    assert is_power_on(schedule, at(1)) is False
    assert next_change(schedule, at(1)) == at(2)
    assert is_power_on(schedule, at(23)) is False
    assert next_change(schedule, at(23)) == at(2, day_offset=1)


def test_adjacent_outages_are_merged():
    schedule = parse_intervals("00:00-04:00, 20:00-24:00")
    assert next_change(schedule, at(23)) == at(4, day_offset=1)


def test_no_outages_power_always_on():
    assert is_power_on([], at(10)) is True
    assert next_change([], at(10)) is None
