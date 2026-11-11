"""REST-ендпоінти. Тонкий шар над app/services."""

from collections.abc import Iterator
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import clock
from app.domain import PowerState
from app.models import Address, Subscription
from app.services import addresses, notifications, reports, schedules
from app.services.address_status import address_status
from app.services.parser import ScheduleParseError, format_intervals

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
def get_status(street: str, house: str, session: SessionDep, now: NowDep) -> dict:
    address = require_address(session, street, house)
    return asdict(address_status(session, address, now))


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
def get_due_notifications(session: SessionDep, now: NowDep) -> list[dict]:
    subs = session.scalars(select(Subscription).order_by(Subscription.id)).all()
    return notifications.due_notifications(subs, schedules.load_intervals(session), now)


class ReportIn(BaseModel):
    user_id: str
    street: str
    house: str
    status: PowerState


@router.post("/reports", status_code=201)
def create_report(data: ReportIn, session: SessionDep, now: NowDep) -> dict:
    address = require_address(session, data.street, data.house)
    try:
        new = reports.NewReport(data.user_id, address.street, address.house, data.status)
        report = reports.add_report(session, new, now)
    except reports.RateLimitError as exc:
        raise HTTPException(429, detail=str(exc)) from exc
    return {
        "id": report.id,
        "user_id": report.user_id,
        "street": report.street,
        "house": report.house,
        "status": report.status,
        "created_at": report.created_at,
    }
