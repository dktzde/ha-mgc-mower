"""Weekly mowing schedule of MGC mowers (R HOME app "appointment").

Format confirmed by capturing the R HOME app with a Redkey MGC1000:

- The app sends the command ``mow_regular`` to the service shadow with the
  complete list of entries (also when only one entry is changed or deleted):
  ``{"value": [entry, ...], "timezone": 2, "timezone_sec": 7200}``.
- The mower stores the plan itself and reports it about one second later in
  the property shadow as ``appointment`` (same envelope).
- One entry per weekday: ``week`` 1 = Monday ... 7 = Sunday (no bitmask),
  ``start_time``/``end_time`` in seconds after local midnight, ``end_time``
  -1 = until finished, ``cutter_height`` in mm, ``cutter_direction``
  1 = perpendicular, 2 = parallel, 3 = cross, ``repeat`` 1 = weekly.
  ``active``, ``unlock`` and ``workmode`` are always 1, 1 and 0 in the app.
"""

from __future__ import annotations

from datetime import time
from typing import Any

from homeassistant.util import dt as dt_util

WEEKDAYS: tuple[str, ...] = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
DIRECTIONS: dict[str, int] = {"perpendicular": 1, "parallel": 2, "cross": 3}
DIRECTION_NAMES: dict[int, str] = {value: key for key, value in DIRECTIONS.items()}
UNTIL_FINISHED = -1
MIN_CUTTER_HEIGHT = 30
MAX_CUTTER_HEIGHT = 70
CUTTER_HEIGHT_STEP = 5


def _seconds(value: time) -> int:
    return value.hour * 3600 + value.minute * 60 + value.second


def _time_text(seconds: Any) -> str | None:
    if isinstance(seconds, bool) or not isinstance(seconds, int) or not 0 <= seconds < 86400:
        return None
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}"


def schedule_entries(state: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Return the schedule reported by the mower in a readable form.

    Returns None if the mower does not report a schedule at all.
    """
    appointment = state.get("appointment")
    if not isinstance(appointment, dict):
        return None
    entries = appointment.get("value")
    if not isinstance(entries, list):
        return None
    result: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        week = entry.get("week")
        end_time = entry.get("end_time")
        direction = entry.get("cutter_direction")
        result.append(
            {
                "weekday": WEEKDAYS[week - 1] if isinstance(week, int) and 1 <= week <= 7 else week,
                "start": _time_text(entry.get("start_time")),
                "end": None if end_time == UNTIL_FINISHED else _time_text(end_time),
                "cutter_height": entry.get("cutter_height"),
                "direction": DIRECTION_NAMES.get(direction, direction),
            }
        )
    return result


def schedule_summary(entries: list[dict[str, Any]]) -> str:
    """Return a short text like ``mon 17:00-19:00 55 mm cross``."""
    return ", ".join(
        f"{entry['weekday']} {entry['start']}-{entry['end'] or 'finished'} "
        f"{entry['cutter_height']} mm {entry['direction']}"
        for entry in entries
    )


def build_schedule_command(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the data of the ``mow_regular`` command like the R HOME app sends it.

    Each entry needs ``weekday`` (one of WEEKDAYS) or ``weekdays`` (list),
    ``start`` (time), optional ``end`` (time, None = until finished),
    ``cutter_height`` (mm) and ``direction`` (one of DIRECTIONS). An empty list
    clears the schedule.

    Raises:
        ValueError: If an entry is incomplete or invalid
    """
    value: list[dict[str, Any]] = []
    for entry in entries:
        weekdays = entry.get("weekdays") or ([entry["weekday"]] if entry.get("weekday") else [])
        if not weekdays:
            raise ValueError("Each schedule entry needs weekday or weekdays")
        start = _seconds(entry["start"])
        end = UNTIL_FINISHED if entry.get("end") is None else _seconds(entry["end"])
        if end != UNTIL_FINISHED and end <= start:
            raise ValueError("The end of a schedule entry must be after its start")
        height = int(entry["cutter_height"])
        if (
            not MIN_CUTTER_HEIGHT <= height <= MAX_CUTTER_HEIGHT
            or height % CUTTER_HEIGHT_STEP
        ):
            raise ValueError(
                f"Cutting height must be {MIN_CUTTER_HEIGHT}-{MAX_CUTTER_HEIGHT} mm "
                f"in steps of {CUTTER_HEIGHT_STEP} mm"
            )
        direction = DIRECTIONS[entry.get("direction", "perpendicular")]
        for weekday in weekdays:
            value.append(
                {
                    "start_time": start,
                    "end_time": end,
                    "repeat": 1,
                    "cutter_height": height,
                    "cutter_direction": direction,
                    "week": WEEKDAYS.index(weekday) + 1,
                    "active": 1,
                    "unlock": 1,
                    "workmode": 0,
                }
            )
    value.sort(key=lambda item: (item["week"], item["start_time"]))

    offset = dt_util.now().utcoffset()
    timezone_sec = int(offset.total_seconds()) if offset is not None else 0
    timezone: int | float = (
        timezone_sec // 3600 if timezone_sec % 3600 == 0 else timezone_sec / 3600
    )
    return {"value": value, "timezone": timezone, "timezone_sec": timezone_sec}
