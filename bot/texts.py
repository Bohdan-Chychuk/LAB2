"""Тексти відповідей бота. Не залежить від aiogram — використовує ті самі сервіси, що й API."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.domain import PowerState
from app.services import addresses, reports, schedules, status

HELP = (
    "Я показую графік відключень світла у Львові.\n"
    "/address <вулиця> <будинок> — запам'ятати адресу, напр. /address Шевченка 10\n"
    "/status — чи є зараз світло і коли наступне відключення"
)


def parse_address(text: str) -> tuple[str, str] | None:
    """ "Шевченка, 10" / "Княгині Ольги 14" -> (вулиця, будинок)."""
    parts = text.replace(",", " ").split()
    if len(parts) < 2:
        return None
    return " ".join(parts[:-1]), parts[-1]


def address_text(session: Session, street: str, house: str) -> str:
    address = addresses.get_address(session, street, house)
    if address is None:
        return f"Адресу не знайдено: {street}, {house}"
    return f"{address.street}, {address.house} — черга {address.queue}"


def status_text(session: Session, street: str, house: str, now: datetime) -> str:
    address = addresses.get_address(session, street, house)
    if address is None:
        return f"Адресу не знайдено: {street}, {house}"
    intervals = schedules.get_intervals(session, address.queue) or []
    on = status.is_power_on(intervals, now)
    lines = [f"{address.street}, {address.house} (черга {address.queue})"]
    lines.append("💡 Світло є" if on else "🌑 Світла немає")
    change = status.next_change(intervals, now)
    if change:
        lines.append(f"{'Відключення' if on else 'Увімкнення'} о {change:%H:%M}")
    outage = status.next_outage(intervals, now)
    if outage:
        lines.append(f"Наступне відключення через {status.minutes_until(outage, now)} хв")
    actual = reports.actual_status(session, address.street, now)
    if actual:
        lines.append(
            f"За репортами сусідів: {'світло є' if actual is PowerState.ON else 'світла немає'}"
        )
    return "\n".join(lines)
