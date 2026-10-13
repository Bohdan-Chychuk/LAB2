"""REST-ендпоінти. Тонкий шар над app/services."""

from collections.abc import Iterator
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Address, Subscription
from app.services import addresses, notifications, reports, schedules, status
from app.services.parser import ScheduleParseError, format_intervals

router = APIRouter()


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def require_address(session: Session, street: str, house: str) -> Address:
    address = addresses.get_address(session, street, house)
    if address is None:
        raise HTTPException(404, detail=f"Адресу не знайдено: {street}, {house}")
    return address


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/streets")
def get_streets(session: SessionDep, q: str = "") -> list[str]:
    return addresses.suggest_streets(session, q)


@router.get("/queue")
def get_queue(street: str, house: str, session: SessionDep) -> dict:
    address = require_address(session, street, house)
    return {"street": address.street, "house": address.house, "queue": address.queue}


@router.post("/schedules/import")
def import_schedule(data: dict, session: SessionDep) -> dict:
    try:
        changed = schedules.import_schedule(session, data)
    except (ScheduleParseError, KeyError, ValueError, AttributeError) as exc:
        raise HTTPException(422, detail=f"Некоректний графік: {exc}") from exc
    return {"changed_queues": changed}


@router.get("/schedule/{queue}")
def get_schedule(queue: int, session: SessionDep) -> dict:
    intervals = schedules.get_intervals(session, queue)
    if intervals is None:
        raise HTTPException(404, detail=f"Графік для черги {queue} не імпортовано")
    return {
        "queue": queue,
        "intervals": [
            dict(zip(("start", "end"), format_intervals([i]).split("-"), strict=True))
            for i in intervals
        ],
    }


@router.get("/status")
def get_status(street: str, house: str, session: SessionDep, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    address = require_address(session, street, house)
    intervals = schedules.get_intervals(session, address.queue) or []
    outage = status.next_outage(intervals, now)
    return {
        "street": address.street,
        "house": address.house,
        "queue": address.queue,
        "now": now,
        "planned": "on" if status.is_power_on(intervals, now) else "off",
        "next_change": status.next_change(intervals, now),
        "next_outage": outage,
        "minutes_to_outage": status.minutes_until(outage, now),
    }


class SubscriptionIn(BaseModel):
    user_id: str
    street: str
    house: str
    notify_before: Literal[15, 30, 60] = 30
    quiet_hours: bool = False


@router.post("/subscriptions", status_code=201)
def create_subscription(data: SubscriptionIn, session: SessionDep) -> dict:
    address = require_address(session, data.street, data.house)
    sub = Subscription(
        user_id=data.user_id,
        street=address.street,
        house=address.house,
        queue=address.queue,
        notify_before=data.notify_before,
        quiet_hours=data.quiet_hours,
    )
    session.add(sub)
    session.commit()
    return {"id": sub.id, **data.model_dump(), "street": sub.street, "queue": sub.queue}


@router.get("/notifications/due")
def get_due_notifications(session: SessionDep, now: datetime | None = None) -> list[dict]:
    subs = session.scalars(select(Subscription).order_by(Subscription.id)).all()
    return notifications.due_notifications(
        subs, schedules.load_intervals(session), now or datetime.now()
    )


class ReportIn(BaseModel):
    user_id: str
    street: str
    house: str
    status: Literal["on", "off"]


@router.post("/reports", status_code=201)
def create_report(data: ReportIn, session: SessionDep, now: datetime | None = None) -> dict:
    address = require_address(session, data.street, data.house)
    report = reports.add_report(
        session, data.user_id, address.street, address.house, data.status, now or datetime.now()
    )
    return {
        "id": report.id,
        "user_id": report.user_id,
        "street": report.street,
        "house": report.house,
        "status": report.status,
        "created_at": report.created_at,
    }
