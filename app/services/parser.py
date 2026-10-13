"""Парсинг графіка відключень у модель «черга → інтервали»."""

import re
from datetime import time

_INTERVAL = re.compile(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$")


class ScheduleParseError(ValueError):
    pass


def parse_intervals(text: str) -> list[tuple[time, time]]:
    result = []
    for part in re.split(r"[,;]", text):
        part = part.strip()
        if not part:
            continue
        match = _INTERVAL.match(part)
        if not match:
            raise ScheduleParseError(f"Некоректний інтервал: {part!r}")
        h1, m1, h2, m2 = map(int, match.groups())
        if h1 > 23 or m1 > 59 or h2 > 24 or m2 > 59 or (h2 == 24 and m2 != 0):
            raise ScheduleParseError(f"Некоректний час: {part!r}")
        start, end = time(h1, m1), time(h2 % 24, m2)
        if start == end:
            raise ScheduleParseError(f"Порожній інтервал: {part!r}")
        result.append((start, end))
    return sorted(result)
