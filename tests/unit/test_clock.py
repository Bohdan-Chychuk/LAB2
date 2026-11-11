"""SVL-34: графіки задані за київським часом, тож «зараз» не може залежати від TZ сервера."""

from datetime import UTC, datetime, timedelta, timezone

from app.clock import now_local, to_local


def test_now_local_converts_utc_to_kyiv_summer_time():
    assert now_local(datetime(2026, 10, 13, 6, 0, tzinfo=UTC)) == datetime(2026, 10, 13, 9, 0)


def test_now_local_converts_utc_to_kyiv_winter_time():
    assert now_local(datetime(2026, 12, 1, 10, 0, tzinfo=UTC)) == datetime(2026, 12, 1, 12, 0)


def test_now_local_returns_naive_datetime():
    assert now_local().tzinfo is None


def test_to_local_keeps_naive_value_as_kyiv_time():
    assert to_local(datetime(2026, 10, 13, 9, 0)) == datetime(2026, 10, 13, 9, 0)


def test_to_local_converts_aware_value_from_other_zone():
    new_york = timezone(timedelta(hours=-4))
    assert to_local(datetime(2026, 10, 13, 2, 0, tzinfo=new_york)) == datetime(2026, 10, 13, 9, 0)
