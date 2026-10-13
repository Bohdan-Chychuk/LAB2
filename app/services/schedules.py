"""Імпорт графіків відключень і виявлення змін відносно попередньої версії."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Schedule
from app.services.parser import Interval, format_intervals, parse_intervals


def normalize_schedule(data: dict) -> dict[int, str]:
    """{"queues": {"1": "08:00-12:00"}} -> {1: "08:00-12:00"} у канонічному форматі."""
    return {int(q): format_intervals(parse_intervals(text)) for q, text in data["queues"].items()}


def diff_schedules(old: dict[int, str], new: dict[int, str]) -> list[int]:
    return sorted(q for q, text in new.items() if old.get(q) != text)


def load_schedules(session: Session) -> dict[int, str]:
    return {s.queue: s.intervals for s in session.scalars(select(Schedule))}


def load_intervals(session: Session) -> dict[int, list[Interval]]:
    return {q: parse_intervals(text) for q, text in load_schedules(session).items()}


def get_intervals(session: Session, queue: int) -> list[Interval] | None:
    schedule = session.get(Schedule, queue)
    return parse_intervals(schedule.intervals) if schedule else None


def import_schedule(session: Session, data: dict) -> list[int]:
    """Зберігає нову версію графіка. Повертає відсортований список змінених черг."""
    new = normalize_schedule(data)
    changed = diff_schedules(load_schedules(session), new)
    for queue in changed:
        schedule = session.get(Schedule, queue)
        if schedule is None:
            session.add(Schedule(queue=queue, intervals=new[queue], version=1))
        else:
            schedule.intervals = new[queue]
            schedule.version += 1
    session.commit()
    return changed
