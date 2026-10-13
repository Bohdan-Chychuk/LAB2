import json
from pathlib import Path

import pytest

from app.services.parser import ScheduleParseError
from app.services.schedules import diff_schedules, import_schedule, load_schedules

DATA = Path(__file__).resolve().parents[2] / "data" / "schedules"


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_diff_without_changes_is_empty():
    old = {1: "08:00-12:00", 2: ""}
    assert diff_schedules(old, dict(old)) == []


def test_diff_returns_changed_and_new_queues_sorted():
    old = {1: "08:00-12:00", 2: "12:00-16:00"}
    new = {1: "08:00-12:00", 2: "13:00-16:00", 3: "00:00-04:00"}
    assert diff_schedules(old, new) == [2, 3]


def test_first_import_marks_all_queues_changed(session):
    assert import_schedule(session, _load("today.json")) == [1, 2, 3, 4, 5, 6]


def test_reimport_same_schedule_returns_empty_list(session):
    import_schedule(session, _load("today.json"))
    assert import_schedule(session, _load("today.json")) == []


def test_reimport_changed_schedule_returns_changed_queue(session):
    import_schedule(session, _load("today.json"))
    assert import_schedule(session, _load("changed.json")) == [3]
    assert load_schedules(session)[3] == "06:00-10:00, 20:00-24:00"


def test_formatting_differences_are_not_changes(session):
    import_schedule(session, {"queues": {"1": "08:00-12:00, 16:00-20:00"}})
    assert import_schedule(session, {"queues": {"1": "16:00 - 20:00; 8:00-12:00"}}) == []


def test_import_invalid_schedule_raises_and_keeps_old(session):
    import_schedule(session, {"queues": {"1": "08:00-12:00"}})
    with pytest.raises(ScheduleParseError):
        import_schedule(session, {"queues": {"1": "зранку"}})
    assert load_schedules(session) == {1: "08:00-12:00"}
