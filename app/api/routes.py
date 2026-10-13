"""REST-ендпоінти. Тонкий шар над app/services."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models import Address
from app.services import addresses, schedules
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
