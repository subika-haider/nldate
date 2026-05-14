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


# --- New tests for all required patterns ---


# 1. Abbreviated months with periods
def test_abbreviated_month_with_period() -> None:
    assert parse("Dec. 1, 2025", today=TODAY) == date(2025, 12, 1)


def test_abbreviated_month_with_period_jan() -> None:
    assert parse("Jan. 15, 2025", today=TODAY) == date(2025, 1, 15)


def test_abbreviated_month_with_period_feb() -> None:
    assert parse("Feb. 28, 2025", today=TODAY) == date(2025, 2, 28)


# 2. YYYY/MM/DD
def test_yyyymmdd_slash() -> None:
    assert parse("2025/12/04", today=TODAY) == date(2025, 12, 4)


# 3. MM.DD.YYYY
def test_mm_dd_yyyy_dots() -> None:
    assert parse("12.04.2025", today=TODAY) == date(2025, 12, 4)


# 4. "the Nth of Month"
def test_the_nth_of_month() -> None:
    assert parse("the 5th of December", today=TODAY) == date(2025, 12, 5)


def test_the_nth_of_month_with_year() -> None:
    assert parse("the 5th of December 2023", today=TODAY) == date(2023, 12, 5)


# 5. "Month the Nth"
def test_month_the_nth() -> None:
    assert parse("December the 5th", today=TODAY) == date(2025, 12, 5)


def test_month_the_nth_with_year() -> None:
    assert parse("December the 5th, 2023", today=TODAY) == date(2023, 12, 5)


# 6. Compound durations with "and"
def test_compound_duration_and_from_today() -> None:
    assert parse("1 year and 2 months from today", today=TODAY) == date(2026, 8, 15)


# 7. "a day/week/month/year ago", "a day/week/month/year from now"
def test_a_day_ago() -> None:
    assert parse("a day ago", today=TODAY) == date(2025, 6, 14)


def test_a_week_ago() -> None:
    assert parse("a week ago", today=TODAY) == date(2025, 6, 8)


def test_a_month_ago() -> None:
    assert parse("a month ago", today=TODAY) == date(2025, 5, 15)


def test_a_year_ago() -> None:
    assert parse("a year ago", today=TODAY) == date(2024, 6, 15)


def test_a_day_from_now() -> None:
    assert parse("a day from now", today=TODAY) == date(2025, 6, 16)


def test_a_week_from_now() -> None:
    assert parse("a week from now", today=TODAY) == date(2025, 6, 22)


# 8. "2 weeks from next Monday"
def test_two_weeks_from_next_monday() -> None:
    assert parse("2 weeks from next Monday", today=TODAY) == date(2025, 6, 30)


# 9. Word numbers in all contexts
def test_five_days_before_december() -> None:
    assert parse("five days before December 1st, 2025", today=TODAY) == date(
        2025, 11, 26
    )


def test_word_number_days_after() -> None:
    assert parse("three days after January 10, 2025", today=TODAY) == date(2025, 1, 13)


# 10. "the day after tomorrow", "the day before yesterday"
def test_the_day_after_tomorrow() -> None:
    assert parse("the day after tomorrow", today=TODAY) == date(2025, 6, 17)


def test_the_day_before_yesterday() -> None:
    assert parse("the day before yesterday", today=TODAY) == date(2025, 6, 13)


def test_day_after_tomorrow_no_the() -> None:
    assert parse("day after tomorrow", today=TODAY) == date(2025, 6, 17)


def test_day_before_yesterday_no_the() -> None:
    assert parse("day before yesterday", today=TODAY) == date(2025, 6, 13)
