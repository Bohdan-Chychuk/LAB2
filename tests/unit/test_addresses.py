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
