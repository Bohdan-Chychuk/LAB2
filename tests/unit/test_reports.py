from datetime import datetime

import pytest

from app.models import Report
from app.services.reports import NewReport, add_report

NOW = datetime(2026, 10, 13, 18, 0)


def test_add_report_saves_status_and_time(session):
    report = add_report(session, NewReport("u1", "Шевченка", "10", "off"), NOW)
    stored = session.get(Report, report.id)
    assert (stored.user_id, stored.street, stored.house) == ("u1", "Шевченка", "10")
    assert stored.status == "off"
    assert stored.created_at == NOW


def test_add_report_rejects_unknown_status(session):
    with pytest.raises(ValueError):
        NewReport("u1", "Шевченка", "10", "maybe")
