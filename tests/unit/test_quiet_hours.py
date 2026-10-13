from datetime import datetime, time
from types import SimpleNamespace

import pytest

from app.services.notifications import due_notifications, in_quiet_hours
from app.services.parser import parse_intervals

NIGHT = {1: parse_intervals("00:00-04:00, 07:30-09:00")}


def sub(quiet_hours, notify_before=60):
    return SimpleNamespace(
        user_id="u1",
        queue=1,
        notify_before=notify_before,
        quiet_hours=quiet_hours,
        street="Шевченка",
        house="10",
    )


@pytest.mark.parametrize(
    ("moment", "expected"),
    [
        (time(23, 0), True),
        (time(3, 0), True),
        (time(6, 59), True),
        (time(7, 0), False),
        (time(22, 59), False),
    ],
)
def test_in_quiet_hours(moment, expected):
    assert in_quiet_hours(moment) is expected


def test_quiet_hours_filter_night_notification():
    now = datetime(2026, 10, 13, 23, 0)
    assert due_notifications([sub(quiet_hours=True)], NIGHT, now) == []


def test_without_quiet_hours_night_notification_is_sent():
    now = datetime(2026, 10, 13, 23, 0)
    assert len(due_notifications([sub(quiet_hours=False)], NIGHT, now)) == 1


def test_quiet_hours_do_not_block_daytime_notification():
    now = datetime(2026, 10, 13, 7, 0)
    assert len(due_notifications([sub(quiet_hours=True, notify_before=30)], NIGHT, now)) == 1
