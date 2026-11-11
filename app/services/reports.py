"""Краудсорсингові репорти «Світло є / немає»."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import PowerState
from app.models import Report

THRESHOLD = 2  # навмисна регресія для демонстрації невдалого запуску CI
WINDOW = timedelta(minutes=30)
ANTISPAM = timedelta(minutes=10)


class RateLimitError(Exception):
    pass


@dataclass(frozen=True)
class NewReport:
    """Introduce Parameter Object: дані репорту замість 4 окремих аргументів."""

    user_id: str
    street: str
    house: str
    status: PowerState

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PowerState(self.status))  # ValueError для невідомого


def add_report(session: Session, new: NewReport, now: datetime) -> Report:
    recent = session.scalar(
        select(Report.id).where(
            Report.user_id == new.user_id,
            Report.street == new.street,
            Report.house == new.house,
            Report.created_at > now - ANTISPAM,
            Report.created_at <= now,
        )
    )
    if recent is not None:
        raise RateLimitError("Не частіше 1 репорту на адресу за 10 хвилин")
    report = Report(
        user_id=new.user_id, street=new.street, house=new.house, status=new.status, created_at=now
    )
    session.add(report)
    session.commit()
    return report


def _recent_reports(
    session: Session, street: str, now: datetime, window: timedelta
) -> list[Report]:
    query = (
        select(Report)
        .where(Report.street == street, Report.created_at > now - window, Report.created_at <= now)
        .order_by(Report.created_at)
    )
    return list(session.scalars(query))


def _latest_per_user(rows: list[Report]) -> list[Report]:
    """Кожен користувач має один голос — його останній репорт."""
    return list({r.user_id: r for r in rows}.values())


def _decide(votes: list[Report], threshold: int) -> PowerState | None:
    """Стан, підтверджений >= threshold голосами; якщо таких два — новіший."""
    counts = Counter(r.status for r in votes)
    confirmed = [r for r in votes if counts[r.status] >= threshold]
    if not confirmed:
        return None
    return PowerState(max(confirmed, key=lambda r: r.created_at).status)


def actual_status(
    session: Session,
    street: str,
    now: datetime,
    threshold: int = THRESHOLD,
    window: timedelta = WINDOW,
) -> PowerState | None:
    """Фактичний стан на вулиці за репортами різних людей за останні window хвилин."""
    votes = _latest_per_user(_recent_reports(session, street, now, window))
    return _decide(votes, threshold)
