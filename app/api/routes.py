"""REST-ендпоінти. Тонкий шар над app/services."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models import Address
from app.services import addresses

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
