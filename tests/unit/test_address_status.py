"""SVL-35: зведений стан адреси — одна функція для API і бота."""

from datetime import datetime

from app.domain import PowerState
from app.models import Address, Report
from app.services.address_status import address_status
from app.services.schedules import import_schedule
from bot.texts import format_status

NOW = datetime(2026, 10, 13, 13, 0)


def test_address_status_combines_schedule_and_reports(session):
    address = Address(street="Шевченка", house="10", queue=2)
    session.add(address)
    import_schedule(session, {"queues": {"2": "12:00-16:00"}})
    for user in ("u1", "u2", "u3"):
        session.add(
            Report(user_id=user, street="Шевченка", house="10", status="on", created_at=NOW)
        )
    session.commit()

    s = address_status(session, address, NOW)

    assert (s.queue, s.planned, s.actual) == (2, PowerState.OFF, PowerState.ON)
    assert s.next_change == datetime(2026, 10, 13, 16, 0)
    assert s.next_outage == datetime(2026, 10, 14, 12, 0)
    assert s.minutes_to_outage == 23 * 60


def test_format_status_renders_all_parts(session):
    address = Address(street="Зелена", house="7", queue=4)
    session.add(address)
    import_schedule(session, {"queues": {"4": "14:00-18:00"}})

    text = format_status(address_status(session, address, NOW))

    assert text.splitlines() == [
        "Зелена, 7 (черга 4)",
        "💡 Світло є",
        "Відключення о 14:00",
        "Наступне відключення через 60 хв",
    ]
