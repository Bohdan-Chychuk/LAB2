"""Пошук черги відключень за адресою."""

from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.domain import normalize, normalize_street
from app.models import Address


def get_address(session: Session, street: str, house: str) -> Address | None:
    query = select(Address).where(
        Address.street_key == normalize_street(street), Address.house_key == normalize(house)
    )
    return session.scalars(query).first()


def find_queue(session: Session, street: str, house: str) -> int | None:
    address = get_address(session, street, house)
    return address.queue if address else None


def suggest_streets(session: Session, query: str, limit: int = 10) -> list[str]:
    """Унікальні назви вулиць, що містять query (без урахування регістру), спершу за префіксом."""
    needle = normalize_street(query) or normalize(query)
    if not needle:
        return []
    not_prefix = case((Address.street_key.startswith(needle, autoescape=True), 0), else_=1)
    rows = session.execute(
        select(Address.street, not_prefix.label("not_prefix"))
        .where(Address.street_key.contains(needle, autoescape=True))
        .distinct()
        .order_by("not_prefix", Address.street)
        .limit(limit)
    )
    return [street for street, _ in rows]
