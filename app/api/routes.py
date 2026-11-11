"""REST-ендпоінти. Тонкий шар над app/services; формати — у app/api/schemas.py."""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import clock
from app.api.schemas import (
    ChangedQueuesOut,
    HealthOut,
    IntervalOut,
    NotificationOut,
    QueueOut,
    ReportIn,
    ReportOut,
    ScheduleIn,
    ScheduleOut,
    StatusOut,
    SubscriptionIn,
    SubscriptionOut,
)
from app.models import Address, Subscription
from app.services import addresses, notifications, reports, schedules
from app.services.address_status import address_status
from app.services.parser import format_interval

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "web" / "templates")


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_now(now: datetime | None = None) -> datetime:
    """Параметр ?now= для демо й тестів; за замовчуванням — поточний київський час."""
    return clock.to_local(now) if now else clock.now_local()


NowDep = Annotated[datetime, Depends(get_now)]


def require_address(session: Session, street: str, house: str) -> Address:
    address = addresses.get_address(session, street, house)
    if address is None:
        raise HTTPException(404, detail=f"Адресу не знайдено: {street}, {house}")
    return address


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@router.get("/health")
def health() -> HealthOut:
    return HealthOut()


@router.get("/streets")
def get_streets(session: SessionDep, q: str = "") -> list[str]:
    return addresses.suggest_streets(session, q)


@router.get("/queue")
def get_queue(street: str, house: str, session: SessionDep) -> QueueOut:
    return QueueOut.model_validate(require_address(session, street, house))


@router.post("/schedules/import")
def import_schedule(data: ScheduleIn, session: SessionDep) -> ChangedQueuesOut:
    return ChangedQueuesOut(changed_queues=schedules.import_schedule(session, data.queues))


@router.get("/schedule/{queue}")
def get_schedule(queue: int, session: SessionDep) -> ScheduleOut:
    intervals = schedules.get_intervals(session, queue)
    if intervals is None:
        raise HTTPException(404, detail=f"Графік для черги {queue} не імпортовано")
    return ScheduleOut(
        queue=queue,
        intervals=[IntervalOut(start=s, end=e) for s, e in map(format_interval, intervals)],
    )


@router.get("/status")
def get_status(street: str, house: str, session: SessionDep, now: NowDep) -> StatusOut:
    address = require_address(session, street, house)
    return StatusOut.model_validate(address_status(session, address, now))


@router.post("/subscriptions", status_code=201)
def create_subscription(data: SubscriptionIn, session: SessionDep) -> SubscriptionOut:
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
    return SubscriptionOut.model_validate(sub)


@router.get("/notifications/due")
def get_due_notifications(session: SessionDep, now: NowDep) -> list[NotificationOut]:
    subs = session.scalars(select(Subscription).order_by(Subscription.id)).all()
    due = notifications.due_notifications(subs, schedules.load_intervals(session), now)
    return [NotificationOut(**n) for n in due]


@router.post("/reports", status_code=201)
def create_report(data: ReportIn, session: SessionDep, now: NowDep) -> ReportOut:
    address = require_address(session, data.street, data.house)
    new = reports.NewReport(data.user_id, address.street, address.house, data.status)
    try:
        report = reports.add_report(session, new, now)
    except reports.RateLimitError as exc:
        raise HTTPException(429, detail=str(exc)) from exc
    return ReportOut.model_validate(report)
