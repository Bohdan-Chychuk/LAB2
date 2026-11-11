from datetime import time

import pytest

from app.services.parser import ScheduleParseError, parse_intervals


def test_parse_regular_intervals():
    assert parse_intervals("08:00-12:00, 16:00-20:00") == [
        (time(8, 0), time(12, 0)),
        (time(16, 0), time(20, 0)),
    ]


def test_parse_sorts_intervals_and_accepts_semicolon_and_spaces():
    assert parse_intervals(" 16:00 - 20:00 ;8:30-12:00 ") == [
        (time(8, 30), time(12, 0)),
        (time(16, 0), time(20, 0)),
    ]


def test_parse_interval_crossing_midnight():
    assert parse_intervals("22:00-02:00") == [(time(22, 0), time(2, 0))]


def test_parse_24_00_means_end_of_day():
    assert parse_intervals("20:00-24:00") == [(time(20, 0), time(0, 0))]


def test_parse_empty_string_means_no_outages():
    assert parse_intervals("") == []


@pytest.mark.parametrize(
    "bad", ["08:00", "8-12", "25:00-26:00", "08:61-09:00", "10:00-10:00", "abc"]
)
def test_parse_invalid_string_raises_parser_error(bad):
    with pytest.raises(ScheduleParseError):
        parse_intervals(bad)


def test_format_interval_returns_start_and_end_strings():
    from app.services.parser import format_interval

    assert format_interval((time(8, 0), time(12, 0))) == ("08:00", "12:00")
    assert format_interval((time(20, 0), time(0, 0))) == ("20:00", "24:00")
