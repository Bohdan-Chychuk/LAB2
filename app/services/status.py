"""Плановий стан світла за графіком черги. Час завжди передається параметром now."""

from datetime import date, datetime, timedelta

from app.services.parser import Interval

Period = tuple[datetime, datetime]


def _periods_for_day(intervals: list[Interval], day: date) -> list[Period]:
    periods = []
    for start, end in intervals:
        end_day = day if end > start else day + timedelta(days=1)
        periods.append((datetime.combine(day, start), datetime.combine(end_day, end)))
    return periods


def outage_periods(intervals: list[Interval], now: datetime) -> list[Period]:
    """Конкретні періоди відключень від учора до післязавтра, суміжні — злиті."""
    raw = []
    for offset in range(-1, 3):
        raw += _periods_for_day(intervals, now.date() + timedelta(days=offset))
    merged: list[Period] = []
    for start, end in sorted(raw):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def is_power_on(intervals: list[Interval], now: datetime) -> bool:
    return not any(start <= now < end for start, end in outage_periods(intervals, now))


def next_change(intervals: list[Interval], now: datetime) -> datetime | None:
    for start, end in outage_periods(intervals, now):
        if start <= now < end:
            return end
        if start > now:
            return start
    return None


def next_outage(intervals: list[Interval], now: datetime) -> datetime | None:
    """Початок найближчого відключення, що починається після now."""
    return next((start for start, _ in outage_periods(intervals, now) if start > now), None)


def minutes_until(moment: datetime | None, now: datetime) -> int | None:
    if moment is None:
        return None
    return int((moment - now).total_seconds() // 60)
