"""Початкове наповнення БД демо-даними з data/."""

import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Address, Schedule
from app.services.schedules import import_schedule

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def seed_addresses(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Address)):
        return
    rows = json.loads((DATA_DIR / "addresses.json").read_text(encoding="utf-8"))
    session.add_all(Address(**row) for row in rows)
    session.commit()


def seed_schedule(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Schedule)):
        return
    data = json.loads((DATA_DIR / "schedules" / "today.json").read_text(encoding="utf-8"))
    import_schedule(session, data)
