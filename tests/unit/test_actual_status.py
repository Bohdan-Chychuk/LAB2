from datetime import datetime, timedelta

from app.services.reports import actual_status, add_report

NOW = datetime(2026, 10, 13, 18, 0)


def add(session, user, status, minutes_ago=0, street="Шевченка", house="10"):
    add_report(session, user, street, house, status, NOW - timedelta(minutes=minutes_ago))


def test_below_threshold_actual_is_unknown(session):
    add(session, "u1", "off")
    add(session, "u2", "off")
    assert actual_status(session, "Шевченка", NOW) is None


def test_three_matching_reports_override_planned(session):
    for user in ("u1", "u2", "u3"):
        add(session, user, "off", minutes_ago=5)
    assert actual_status(session, "Шевченка", NOW) == "off"


def test_reports_from_other_houses_on_same_street_count(session):
    add(session, "u1", "on", house="10")
    add(session, "u2", "on", house="25")
    add(session, "u3", "on", house="48")
    assert actual_status(session, "Шевченка", NOW) == "on"


def test_old_reports_are_not_counted(session):
    add(session, "u1", "off", minutes_ago=31)
    add(session, "u2", "off", minutes_ago=40)
    add(session, "u3", "off", minutes_ago=1)
    assert actual_status(session, "Шевченка", NOW) is None


def test_other_streets_are_not_counted(session):
    add(session, "u1", "off")
    add(session, "u2", "off")
    add(session, "u3", "off", street="Зелена", house="7")
    assert actual_status(session, "Шевченка", NOW) is None


def test_latest_report_of_each_user_counts_once(session):
    add(session, "u1", "off", minutes_ago=20)
    add(session, "u1", "on", minutes_ago=5, house="25")
    add(session, "u2", "off")
    add(session, "u3", "off")
    assert actual_status(session, "Шевченка", NOW) is None


def test_when_both_reach_threshold_most_recent_wins(session):
    for i, user in enumerate(("a", "b", "c")):
        add(session, user, "off", minutes_ago=25 - i)
    for i, user in enumerate(("d", "e", "f")):
        add(session, user, "on", minutes_ago=5 - i)
    assert actual_status(session, "Шевченка", NOW) == "on"
