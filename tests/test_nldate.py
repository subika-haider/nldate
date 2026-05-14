"""Tests for nldate.parse()."""

from datetime import date

from nldate import parse

TODAY = date(2025, 6, 15)  # A Sunday


def test_today() -> None:
    assert parse("today", today=TODAY) == TODAY


def test_tomorrow() -> None:
    assert parse("tomorrow", today=TODAY) == date(2025, 6, 16)


def test_yesterday() -> None:
    assert parse("yesterday", today=TODAY) == date(2025, 6, 14)


def test_absolute_month_day_year() -> None:
    assert parse("December 1st, 2025", today=TODAY) == date(2025, 12, 1)


def test_absolute_month_day_year_no_ordinal() -> None:
    assert parse("December 1, 2025", today=TODAY) == date(2025, 12, 1)


def test_iso_format() -> None:
    assert parse("2025-12-01", today=TODAY) == date(2025, 12, 1)


def test_days_before() -> None:
    assert parse("5 days before December 1st, 2025", today=TODAY) == date(2025, 11, 26)


def test_days_after() -> None:
    assert parse("3 days after January 10, 2025", today=TODAY) == date(2025, 1, 13)


def test_next_tuesday() -> None:
    assert parse("next Tuesday", today=TODAY) == date(2025, 6, 17)


def test_last_friday() -> None:
    assert parse("last Friday", today=TODAY) == date(2025, 6, 13)


def test_in_3_days() -> None:
    assert parse("in 3 days", today=TODAY) == date(2025, 6, 18)


def test_2_weeks_ago() -> None:
    assert parse("2 weeks ago", today=TODAY) == date(2025, 6, 1)


def test_year_and_months_after() -> None:
    assert parse("1 year and 2 months after yesterday", today=TODAY) == date(
        2026, 8, 14
    )


def test_from_tomorrow() -> None:
    assert parse("3 days from tomorrow", today=TODAY) == date(2025, 6, 19)


def test_next_week() -> None:
    assert parse("next week", today=TODAY) == date(2025, 6, 22)


def test_day_month_year() -> None:
    assert parse("1 December 2025", today=TODAY) == date(2025, 12, 1)
