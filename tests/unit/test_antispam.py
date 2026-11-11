from datetime import datetime, timedelta

import pytest

from app.services.reports import NewReport, RateLimitError, add_report

NOW = datetime(2026, 10, 13, 18, 0)


def test_second_report_within_10_minutes_is_rejected(session):
    add_report(session, NewReport("u1", "Шевченка", "10", "off"), NOW)
    with pytest.raises(RateLimitError):
        add_report(session, NewReport("u1", "Шевченка", "10", "on"), NOW + timedelta(minutes=9))


def test_report_after_10_minutes_is_allowed(session):
    add_report(session, NewReport("u1", "Шевченка", "10", "off"), NOW)
    add_report(session, NewReport("u1", "Шевченка", "10", "on"), NOW + timedelta(minutes=10))


def test_limit_is_per_user_and_address(session):
    add_report(session, NewReport("u1", "Шевченка", "10", "off"), NOW)
    add_report(session, NewReport("u2", "Шевченка", "10", "off"), NOW)
    add_report(session, NewReport("u1", "Зелена", "7", "off"), NOW)
