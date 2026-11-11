"""Тексти відповідей бота. Не залежить від aiogram — використовує ті самі сервіси, що й API."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.domain import PowerState
from app.services import addresses
from app.services.address_status import AddressStatus, address_status

HELP = (
    "Я показую графік відключень світла у Львові.\n"
    "/address <вулиця> <будинок> — запам'ятати адресу, напр. /address Шевченка 10\n"
    "/status — чи є зараз світло і коли наступне відключення"
)
ACTUAL_TEXT = {PowerState.ON: "світло є", PowerState.OFF: "світла немає"}


def parse_address(text: str) -> tuple[str, str] | None:
    """ "Шевченка, 10" / "Княгині Ольги 14" -> (вулиця, будинок)."""
    parts = text.replace(",", " ").split()
    if len(parts) < 2:
        return None
    return " ".join(parts[:-1]), parts[-1]


def not_found(street: str, house: str) -> str:
    return f"Адресу не знайдено: {street}, {house}"


def address_text(session: Session, street: str, house: str) -> str:
    address = addresses.get_address(session, street, house)
    if address is None:
        return not_found(street, house)
    return f"{address.street}, {address.house} — черга {address.queue}"


def format_status(s: AddressStatus) -> str:
    lines = [
        f"{s.street}, {s.house} (черга {s.queue})",
        "💡 Світло є" if s.is_on else "🌑 Світла немає",
    ]
    if s.next_change:
        lines.append(f"{'Відключення' if s.is_on else 'Увімкнення'} о {s.next_change:%H:%M}")
    if s.next_outage:
        lines.append(f"Наступне відключення через {s.minutes_to_outage} хв")
    if s.actual:
        lines.append(f"За репортами сусідів: {ACTUAL_TEXT[s.actual]}")
    return "\n".join(lines)


def status_text(session: Session, street: str, house: str, now: datetime) -> str:
    address = addresses.get_address(session, street, house)
    if address is None:
        return not_found(street, house)
    return format_status(address_status(session, address, now))
