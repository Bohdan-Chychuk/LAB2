"""Пошук черги відключень за адресою."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Address

_STREET_PREFIX = re.compile(r"^(вул\.|вулиця|просп\.|проспект|пл\.|площа)\s*", re.IGNORECASE)


def normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def normalize_street(street: str) -> str:
    return _STREET_PREFIX.sub("", normalize(street))


def get_address(session: Session, street: str, house: str) -> Address | None:
    street_key, house_key = normalize_street(street), normalize(house)
    for address in session.scalars(select(Address)):
        if normalize(address.street) == street_key and normalize(address.house) == house_key:
            return address
    return None


def find_queue(session: Session, street: str, house: str) -> int | None:
    address = get_address(session, street, house)
    return address.queue if address else None


def suggest_streets(session: Session, query: str, limit: int = 10) -> list[str]:
    """Унікальні назви вулиць, що містять query (без урахування регістру), спершу за префіксом."""
    needle = normalize_street(query) or normalize(query)
    if not needle:
        return []
    streets = {a.street for a in session.scalars(select(Address))}
    matches = [s for s in streets if needle in normalize(s)]
    matches.sort(key=lambda s: (not normalize(s).startswith(needle), s))
    return matches[:limit]
