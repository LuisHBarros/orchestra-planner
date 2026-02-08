"""Domain services (lazy imports to avoid circular dependencies)."""

from typing import Any

__all__ = [
    "ScheduleCalculator",
    "TaskSchedule",
    "FixedTimeProvider",
    "SystemTimeProvider",
]


def __getattr__(name: str) -> Any:
    if name in ("ScheduleCalculator", "TaskSchedule"):
        from backend.src.domain.services.schedule_calculator import (
            ScheduleCalculator,
            TaskSchedule,
        )

        return {"ScheduleCalculator": ScheduleCalculator, "TaskSchedule": TaskSchedule}[
            name
        ]
    if name in ("FixedTimeProvider", "SystemTimeProvider"):
        from backend.src.domain.services.time_provider import (
            FixedTimeProvider,
            SystemTimeProvider,
        )

        return {
            "FixedTimeProvider": FixedTimeProvider,
            "SystemTimeProvider": SystemTimeProvider,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
