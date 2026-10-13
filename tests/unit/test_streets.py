import pytest
from app.services.addresses import suggest_streets

from app.models import Address


@pytest.fixture
def streets(session):
    names = ["Шевченка", "Шептицьких", "Шкільна", "Городоцька", "Зелена"]
    session.add_all([Address(street=n, house=str(i), queue=1) for i, n in enumerate(names)])
    session.add(Address(street="Шевченка", house="99", queue=2))
    session.commit()
    return session


def test_suggest_streets_matches_prefix_case_insensitive(streets):
    assert suggest_streets(streets, "шев") == ["Шевченка"]


def test_suggest_streets_returns_unique_sorted_matches(streets):
    assert suggest_streets(streets, "Ш") == ["Шевченка", "Шептицьких", "Шкільна"]


def test_suggest_streets_matches_substring(streets):
    assert suggest_streets(streets, "одоц") == ["Городоцька"]


def test_suggest_streets_empty_query_returns_nothing(streets):
    assert suggest_streets(streets, "  ") == []


def test_suggest_streets_limits_result(session):
    session.add_all([Address(street=f"Вулиця {i:02d}", house="1", queue=1) for i in range(15)])
    session.commit()
    assert len(suggest_streets(session, "вулиця")) == 10
