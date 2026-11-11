"""Зведений стан світла для адреси: графік + репорти. Спільний для REST API і Telegram-бота."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain import PowerState
from app.models import Address
from app.services import reports, schedules, status


@dataclass(frozen=True)
class AddressStatus:
    street: str
    house: str
    queue: int
    now: datetime
    planned: PowerState
    next_change: datetime | None
    next_outage: datetime | None
    minutes_to_outage: int | None
    actual: PowerState | None

    @property
    def is_on(self) -> bool:
        return self.planned is PowerState.ON


def address_status(session: Session, address: Address, now: datetime) -> AddressStatus:
    intervals = schedules.get_intervals(session, address.queue) or []
    outage = status.next_outage(intervals, now)
    return AddressStatus(
        street=address.street,
        house=address.house,
        queue=address.queue,
        now=now,
        planned=PowerState.from_power(status.is_power_on(intervals, now)),
        next_change=status.next_change(intervals, now),
        next_outage=outage,
        minutes_to_outage=status.minutes_until(outage, now),
        actual=reports.actual_status(session, address.street, now),
    )
