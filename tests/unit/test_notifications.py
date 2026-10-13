from datetime import datetime
from types import SimpleNamespace

from app.services.notifications import due_notifications
from app.services.parser import parse_intervals

SCHEDULES = {1: parse_intervals("16:00-20:00"), 2: []}


def sub(user_id="u1", queue=1, notify_before=30, quiet_hours=False):
    return SimpleNamespace(
        user_id=user_id,
        queue=queue,
        notify_before=notify_before,
        quiet_hours=quiet_hours,
        street="Шевченка",
        house="10",
    )


def at(hour, minute=0):
    return datetime(2026, 10, 13, hour, minute)


def test_notification_due_exactly_n_minutes_before_outage():
    due = due_notifications([sub()], SCHEDULES, at(15, 30))
    assert len(due) == 1
    assert due[0]["user_id"] == "u1"
    assert due[0]["outage_start"] == at(16)


def test_notification_due_within_two_minute_window():
    assert len(due_notifications([sub()], SCHEDULES, at(15, 32))) == 1
    assert len(due_notifications([sub()], SCHEDULES, at(15, 28))) == 1


def test_notification_not_due_outside_window():
    assert due_notifications([sub()], SCHEDULES, at(15, 33)) == []
    assert due_notifications([sub()], SCHEDULES, at(15, 0)) == []


def test_each_subscription_uses_its_own_lead_time():
    subs = [sub("a", notify_before=15), sub("b", notify_before=60)]
    assert [n["user_id"] for n in due_notifications(subs, SCHEDULES, at(15, 0))] == ["b"]
    assert [n["user_id"] for n in due_notifications(subs, SCHEDULES, at(15, 45))] == ["a"]


def test_queue_without_outages_gets_no_notifications():
    assert due_notifications([sub(queue=2)], SCHEDULES, at(15, 30)) == []
