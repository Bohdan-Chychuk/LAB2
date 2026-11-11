import pytest

from app.models import Address
from app.services.addresses import find_queue


@pytest.fixture
def addresses(session):
    session.add_all(
        [
            Address(street="Шевченка", house="10", queue=3),
            Address(street="Городоцька", house="120", queue=1),
            Address(street="Наукова", house="7А", queue=5),
        ]
    )
    session.commit()
    return session


def test_find_queue_returns_queue_for_known_address(addresses):
    assert find_queue(addresses, "Шевченка", "10") == 3


def test_find_queue_ignores_case_extra_spaces_and_street_prefix(addresses):
    assert find_queue(addresses, "  вул.  шевченка ", " 10") == 3


def test_find_queue_house_letter_is_case_insensitive(addresses):
    assert find_queue(addresses, "Наукова", "7а") == 5


def test_find_queue_unknown_address_returns_none(addresses):
    assert find_queue(addresses, "Шевченка", "999") is None
    assert find_queue(addresses, "Неіснуюча", "1") is None


def test_address_keys_are_filled_automatically():
    address = Address(street="Княгині  Ольги", house="14А", queue=4)
    assert (address.street_key, address.house_key) == ("княгині ольги", "14а")


def test_find_queue_uses_indexed_query(addresses):
    statements = []
    engine = addresses.get_bind()
    from sqlalchemy import event

    def log(*args):
        statements.append(args[2])

    event.listen(engine, "before_cursor_execute", log)
    try:
        assert find_queue(addresses, "шевченка", "10") == 3
    finally:
        event.remove(engine, "before_cursor_execute", log)
    assert len(statements) == 1
    assert "street_key = ?" in statements[0]
