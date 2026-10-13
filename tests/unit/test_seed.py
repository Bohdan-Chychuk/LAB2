from sqlalchemy import func, select

from app.models import Address
from app.seed import seed_addresses, seed_schedule
from app.services.schedules import load_schedules


def test_seed_addresses_is_idempotent(session):
    seed_addresses(session)
    count = session.scalar(select(func.count()).select_from(Address))
    seed_addresses(session)
    assert count >= 25
    assert session.scalar(select(func.count()).select_from(Address)) == count


def test_seed_schedule_loads_six_queues_once(session):
    seed_schedule(session)
    seed_schedule(session)
    schedules = load_schedules(session)
    assert sorted(schedules) == [1, 2, 3, 4, 5, 6]
    assert schedules[1] == "08:00-12:00, 16:00-20:00"
