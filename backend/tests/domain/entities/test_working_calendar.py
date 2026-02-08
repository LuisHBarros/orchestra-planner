"""Tests for WorkingCalendar value object."""

from datetime import date, datetime, timezone

from backend.src.domain.entities import WorkingCalendar


def test_is_working_day_respects_timezone_and_exclusions():
    calendar = WorkingCalendar(
        timezone="America/Sao_Paulo",
        exclusion_dates=frozenset({date(2024, 1, 2)}),
    )

    # 2024-01-02 12:00 UTC is 09:00 on 2024-01-02 in Sao Paulo
    excluded_dt = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    assert calendar.is_working_day(excluded_dt) is False

    # 2024-01-02 01:00 UTC is 22:00 on 2024-01-01 in Sao Paulo (not excluded)
    prior_local_dt = datetime(2024, 1, 2, 1, 0, 0, tzinfo=timezone.utc)
    assert calendar.is_working_day(prior_local_dt) is True
