"""Краудсорсингові репорти «Світло є / немає»."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Report

STATUSES = ("on", "off")


def add_report(
    session: Session, user_id: str, street: str, house: str, status: str, now: datetime
) -> Report:
    if status not in STATUSES:
        raise ValueError(f"Невідомий статус: {status!r}")
    report = Report(user_id=user_id, street=street, house=house, status=status, created_at=now)
    session.add(report)
    session.commit()
    return report
