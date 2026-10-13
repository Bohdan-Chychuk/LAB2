"""Краудсорсингові репорти «Світло є / немає»."""

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Report

STATUSES = ("on", "off")
THRESHOLD = 3
WINDOW = timedelta(minutes=30)
ANTISPAM = timedelta(minutes=10)


class RateLimitError(Exception):
    pass


def add_report(
    session: Session, user_id: str, street: str, house: str, status: str, now: datetime
) -> Report:
    if status not in STATUSES:
        raise ValueError(f"Невідомий статус: {status!r}")
    recent = session.scalar(
        select(Report.id).where(
            Report.user_id == user_id,
            Report.street == street,
            Report.house == house,
            Report.created_at > now - ANTISPAM,
            Report.created_at <= now,
        )
    )
    if recent is not None:
        raise RateLimitError("Не частіше 1 репорту на адресу за 10 хвилин")
    report = Report(user_id=user_id, street=street, house=house, status=status, created_at=now)
    session.add(report)
    session.commit()
    return report


def actual_status(
    session: Session,
    street: str,
    now: datetime,
    threshold: int = THRESHOLD,
    window: timedelta = WINDOW,
) -> str | None:
    """Фактичний стан на вулиці: >= threshold однакових репортів різних людей за window."""
    rows = session.scalars(
        select(Report)
        .where(Report.street == street, Report.created_at > now - window, Report.created_at <= now)
        .order_by(Report.created_at)
    ).all()
    latest = {r.user_id: r for r in rows}  # останній репорт кожного користувача
    counts = Counter(r.status for r in latest.values())
    winners = [s for s, c in counts.items() if c >= threshold]
    if len(winners) <= 1:
        return winners[0] if winners else None
    return max(
        (r for r in latest.values() if r.status in winners), key=lambda r: r.created_at
    ).status
