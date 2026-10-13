"""Планування сповіщень за N хвилин до відключення."""

from collections.abc import Iterable
from datetime import datetime, time, timedelta

from app.services.parser import Interval
from app.services.status import next_outage

WINDOW = timedelta(minutes=2)
QUIET_START = time(23, 0)
QUIET_END = time(7, 0)


def in_quiet_hours(moment: time) -> bool:
    return moment >= QUIET_START or moment < QUIET_END


def due_notifications(
    subscriptions: Iterable,
    schedules: dict[int, list[Interval]],
    now: datetime,
    window: timedelta = WINDOW,
) -> list[dict]:
    """Підписки, яким саме зараз (±window) треба надіслати сповіщення."""
    due = []
    quiet_now = in_quiet_hours(now.time())
    for sub in subscriptions:
        if sub.quiet_hours and quiet_now:
            continue
        outage = next_outage(schedules.get(sub.queue, []), now)
        if outage is None:
            continue
        notify_at = outage - timedelta(minutes=sub.notify_before)
        if abs(now - notify_at) <= window:
            due.append(
                {
                    "user_id": sub.user_id,
                    "street": sub.street,
                    "house": sub.house,
                    "queue": sub.queue,
                    "notify_before": sub.notify_before,
                    "outage_start": outage,
                }
            )
    return due
