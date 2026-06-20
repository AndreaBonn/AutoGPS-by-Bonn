"""Test comportamentali del parser opening_hours -> schedule."""

from ztl.schedule import parse_opening_hours


def test_24_7_is_always_active():
    schedule, always = parse_opening_hours("24/7")
    assert always is True
    assert schedule == []


def test_full_week_full_day_is_always_active():
    schedule, always = parse_opening_hours("Mo-Su 00:00-24:00")
    assert always is True
    assert schedule == []


def test_single_weekday_range():
    schedule, always = parse_opening_hours("Mo-Fr 07:30-20:00")
    assert always is False
    assert schedule == [{"days": [1, 2, 3, 4, 5], "from": "07:30", "to": "20:00"}]


def test_multiple_rules_separated_by_semicolon():
    schedule, always = parse_opening_hours("Mo-Fr 07:30-20:00; Sa 07:30-16:00")
    assert always is False
    assert {"days": [1, 2, 3, 4, 5], "from": "07:30", "to": "20:00"} in schedule
    assert {"days": [6], "from": "07:30", "to": "16:00"} in schedule


def test_multiple_time_ranges_expand_to_multiple_entries():
    schedule, _ = parse_opening_hours("Mo-Fr 07:00-10:00,16:00-19:00")
    assert schedule == [
        {"days": [1, 2, 3, 4, 5], "from": "07:00", "to": "10:00"},
        {"days": [1, 2, 3, 4, 5], "from": "16:00", "to": "19:00"},
    ]


def test_comma_day_list():
    schedule, _ = parse_opening_hours("Mo,We,Fr 08:00-18:00")
    assert schedule == [{"days": [1, 3, 5], "from": "08:00", "to": "18:00"}]


def test_weekend_wrap_day_range():
    schedule, _ = parse_opening_hours("Sa-Mo 10:00-12:00")
    assert schedule[0]["days"] == [1, 6, 7]


def test_empty_string_returns_none():
    assert parse_opening_hours("") is None


def test_unsupported_syntax_returns_none():
    assert parse_opening_hours("Mo-Fr sunrise-sunset") is None
    assert parse_opening_hours("PH off") is None


def test_invalid_time_returns_none():
    assert parse_opening_hours("Mo-Fr 25:00-26:00") is None
