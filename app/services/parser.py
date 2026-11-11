"""Парсинг графіка відключень у модель «черга → інтервали».

Інтервал — час відключення (start, end). Якщо end <= start, інтервал перетинає опівніч;
"24:00" трактується як кінець доби (time(0, 0)).
"""

import re
from datetime import time

Interval = tuple[time, time]

_INTERVAL = re.compile(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$")
_SEPARATORS = re.compile(r"[,;]")


class ScheduleParseError(ValueError):
    pass


def _to_time(hour: int, minute: int, *, allow_24: bool, raw: str) -> time:
    if minute > 59 or hour > 24 or (hour == 24 and (minute or not allow_24)):
        raise ScheduleParseError(f"Некоректний час у {raw!r}")
    return time(hour % 24, minute)


def _parse_one(raw: str) -> Interval:
    match = _INTERVAL.match(raw)
    if not match:
        raise ScheduleParseError(f"Некоректний інтервал: {raw!r}")
    h1, m1, h2, m2 = map(int, match.groups())
    start = _to_time(h1, m1, allow_24=False, raw=raw)
    end = _to_time(h2, m2, allow_24=True, raw=raw)
    if start == end:
        raise ScheduleParseError(f"Порожній інтервал: {raw!r}")
    return start, end


def parse_intervals(text: str) -> list[Interval]:
    parts = (p.strip() for p in _SEPARATORS.split(text))
    return sorted(_parse_one(p) for p in parts if p)


def _fmt(value: time, *, is_end: bool) -> str:
    return "24:00" if is_end and value == time(0, 0) else value.strftime("%H:%M")


def format_interval(interval: Interval) -> tuple[str, str]:
    """(time(20, 0), time(0, 0)) -> ("20:00", "24:00")."""
    start, end = interval
    return _fmt(start, is_end=False), _fmt(end, is_end=True)


def format_intervals(intervals: list[Interval]) -> str:
    """Канонічний рядок графіка: "08:00-12:00, 16:00-20:00"."""
    return ", ".join("-".join(format_interval(i)) for i in intervals)
