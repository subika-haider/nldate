"""Natural-language date parser."""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
    "oct": 10, "nov": 11, "dec": 12,
}

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
    "mon": 0, "tue": 1, "tues": 1, "wed": 2, "thu": 3, "thur": 3,
    "thurs": 3, "fri": 4, "sat": 5, "sun": 6,
}

WORD_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "a": 1, "an": 1,
}

ORDINAL_MAP = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
    "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
    "nineteenth": 19, "twentieth": 20, "twenty-first": 21, "twenty-second": 22,
    "twenty-third": 23, "twenty-fourth": 24, "twenty-fifth": 25,
    "twenty-sixth": 26, "twenty-seventh": 27, "twenty-eighth": 28,
    "twenty-ninth": 29, "thirtieth": 30, "thirty-first": 31,
}


def _parse_number(s: str) -> int | None:
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    if s in WORD_NUMBERS:
        return WORD_NUMBERS[s]
    parts = re.split(r"[\s-]+", s)
    if len(parts) == 2 and parts[0] in WORD_NUMBERS and parts[1] in WORD_NUMBERS:
        return WORD_NUMBERS[parts[0]] + WORD_NUMBERS[parts[1]]
    return None


def _parse_ordinal(s: str) -> int | None:
    s = s.strip().lower()
    if s in ORDINAL_MAP:
        return ORDINAL_MAP[s]
    m = re.match(r"^(\d+)(?:st|nd|rd|th)$", s)
    if m:
        return int(m.group(1))
    return None


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def _next_weekday(today: date, weekday: int) -> date:
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def _last_weekday(today: date, weekday: int) -> date:
    days_behind = today.weekday() - weekday
    if days_behind <= 0:
        days_behind += 7
    return today - timedelta(days=days_behind)


def _resolve_anchor(s: str, today: date) -> date | None:
    s = s.strip().lower()
    if s in ("today", "now"):
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)
    return _try_parse_absolute(s, today)


def _try_parse_absolute(s: str, today: date) -> date | None:
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", s)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    s_lower = s.lower().strip().rstrip(".")
    m = re.match(r"^([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})$", s_lower)
    if m and m.group(1) in MONTHS:
        return date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    m = re.match(r"^([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?$", s_lower)
    if m and m.group(1) in MONTHS:
        return date(today.year, MONTHS[m.group(1)], int(m.group(2)))
    m = re.match(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+),?\s*(\d{4})$", s_lower)
    if m and m.group(2) in MONTHS:
        return date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
    m = re.match(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)$", s_lower)
    if m and m.group(2) in MONTHS:
        return date(today.year, MONTHS[m.group(2)], int(m.group(1)))
    m = re.match(r"^([a-z]+)\s+(\d{4})$", s_lower)
    if m and m.group(1) in MONTHS:
        return date(int(m.group(2)), MONTHS[m.group(1)], 1)
    m = re.match(r"^(?:the\s+)?(\w+(?:-\w+)?)\s+of\s+([a-z]+),?\s*(\d{4})$", s_lower)
    if m and m.group(2) in MONTHS:
        day_val = _parse_ordinal(m.group(1))
        if day_val:
            return date(int(m.group(3)), MONTHS[m.group(2)], day_val)
    m = re.match(r"^(?:the\s+)?(\w+(?:-\w+)?)\s+of\s+([a-z]+)$", s_lower)
    if m and m.group(2) in MONTHS:
        day_val = _parse_ordinal(m.group(1))
        if day_val:
            return date(today.year, MONTHS[m.group(2)], day_val)
    m = re.match(r"^([a-z]+)\s+(\w+(?:-\w+)?),?\s*(\d{4})$", s_lower)
    if m and m.group(1) in MONTHS:
        day_val = _parse_ordinal(m.group(2))
        if day_val:
            return date(int(m.group(3)), MONTHS[m.group(1)], day_val)
    m = re.match(r"^([a-z]+)\s+(\w+(?:-\w+)?)$", s_lower)
    if m and m.group(1) in MONTHS:
        day_val = _parse_ordinal(m.group(2))
        if day_val:
            return date(today.year, MONTHS[m.group(1)], day_val)
    return None


def _parse_duration_parts(s: str) -> tuple[int, int, int, int]:
    s = s.strip().lower()
    years = 0
    months = 0
    weeks = 0
    days = 0
    for m in re.finditer(
        r"(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
        r"eighteen|nineteen|twenty|thirty|forty|fifty)\s+"
        r"(year|month|week|day|yr|mo)s?",
        s,
    ):
        n = _parse_number(m.group(1))
        if n is None:
            n = 1
        unit = m.group(2)
        if unit in ("year", "yr"):
            years += n
        elif unit in ("month", "mo"):
            months += n
        elif unit == "week":
            weeks += n
        elif unit == "day":
            days += n
    return years, months, weeks, days


def parse(s: str, today: date | None = None) -> date:
    """Parse a natural-language date string into a date object."""
    if today is None:
        today = date.today()
    original = s
    s = s.strip()
    result = _try_parse_absolute(s, today)
    if result is not None:
        return result
    s_lower = s.lower().strip()
    if s_lower in ("today", "now"):
        return today
    if s_lower == "tomorrow":
        return today + timedelta(days=1)
    if s_lower == "yesterday":
        return today - timedelta(days=1)
    if s_lower in ("the day after tomorrow", "day after tomorrow"):
        return today + timedelta(days=2)
    if s_lower in ("the day before yesterday", "day before yesterday"):
        return today - timedelta(days=2)
    m = re.match(r"^next\s+(\w+)$", s_lower)
    if m and m.group(1) in WEEKDAYS:
        return _next_weekday(today, WEEKDAYS[m.group(1)])
    m = re.match(r"^last\s+(\w+)$", s_lower)
    if m and m.group(1) in WEEKDAYS:
        return _last_weekday(today, WEEKDAYS[m.group(1)])
    if s_lower == "next week":
        return today + timedelta(weeks=1)
    if s_lower == "last week":
        return today - timedelta(weeks=1)
    if s_lower == "next month":
        return _add_months(today, 1)
    if s_lower == "last month":
        return _add_months(today, -1)
    if s_lower == "next year":
        return _add_years(today, 1)
    if s_lower == "last year":
        return _add_years(today, -1)
    m = re.match(
        r"^(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
        r"eighteen|nineteen|twenty|thirty|forty|fifty)"
        r"\s+(year|month|week|day|yr|mo)s?\s+ago$",
        s_lower,
    )
    if m:
        n = _parse_number(m.group(1))
        if n is None:
            n = 1
        unit = m.group(2)
        if unit == "day":
            return today - timedelta(days=n)
        if unit == "week":
            return today - timedelta(weeks=n)
        if unit in ("month", "mo"):
            return _add_months(today, -n)
        if unit in ("year", "yr"):
            return _add_years(today, -n)
    m = re.match(
        r"^in\s+(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
        r"eighteen|nineteen|twenty|thirty|forty|fifty)"
        r"\s+(year|month|week|day|yr|mo)s?$",
        s_lower,
    )
    if m:
        n = _parse_number(m.group(1))
        if n is None:
            n = 1
        unit = m.group(2)
        if unit == "day":
            return today + timedelta(days=n)
        if unit == "week":
            return today + timedelta(weeks=n)
        if unit in ("month", "mo"):
            return _add_months(today, n)
        if unit in ("year", "yr"):
            return _add_years(today, n)
    m = re.match(r"^(.+?)\s+from\s+(.+)$", s_lower)
    if m:
        duration_str = m.group(1)
        anchor_str = m.group(2)
        anchor = _resolve_anchor(anchor_str, today)
        if anchor is not None:
            years, months, weeks, days = _parse_duration_parts(duration_str)
            result = anchor
            if years:
                result = _add_years(result, years)
            if months:
                result = _add_months(result, months)
            result += timedelta(weeks=weeks, days=days)
            return result
    m = re.match(r"^(.+?)\s+after\s+(.+)$", s_lower)
    if m:
        duration_str = m.group(1)
        anchor_str = m.group(2)
        anchor = _resolve_anchor(anchor_str, today)
        if anchor is not None:
            years, months, weeks, days = _parse_duration_parts(duration_str)
            result = anchor
            if years:
                result = _add_years(result, years)
            if months:
                result = _add_months(result, months)
            result += timedelta(weeks=weeks, days=days)
            return result
    m = re.match(r"^(.+?)\s+before\s+(.+)$", s_lower)
    if m:
        duration_str = m.group(1)
        anchor_str = m.group(2)
        anchor = _resolve_anchor(anchor_str, today)
        if anchor is not None:
            years, months, weeks, days = _parse_duration_parts(duration_str)
            result = anchor
            if years:
                result = _add_years(result, -years)
            if months:
                result = _add_months(result, -months)
            result -= timedelta(weeks=weeks, days=days)
            return result
    m = re.match(r"^(.+?)\s+later$", s_lower)
    if m:
        duration_str = m.group(1)
        years, months, weeks, days = _parse_duration_parts(duration_str)
        result = today
        if years:
            result = _add_years(result, years)
        if months:
            result = _add_months(result, months)
        result += timedelta(weeks=weeks, days=days)
        return result
    m = re.match(r"^this\s+(\w+)$", s_lower)
    if m and m.group(1) in WEEKDAYS:
        return _next_weekday(today, WEEKDAYS[m.group(1)])
    m = re.match(r"^a\s+week\s+from\s+(\w+)$", s_lower)
    if m and m.group(1) in WEEKDAYS:
        next_wd = _next_weekday(today, WEEKDAYS[m.group(1)])
        return next_wd + timedelta(weeks=1)
    raise ValueError(f"Cannot parse date: {original!r}")
