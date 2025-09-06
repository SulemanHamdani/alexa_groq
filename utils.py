"""Small utilities shared across modules."""

from __future__ import annotations

from typing import Any, Optional, Callable


def get_slot(event: dict[str, Any], name: str) -> Optional[str]:
    """Safely extract a slot value by name from an Alexa event."""
    try:
        return event["request"]["intent"]["slots"][name]["value"]  # type: ignore[return-value]
    except Exception:
        return None


def get_remaining_ms(context: Any) -> int:
    """Return remaining milliseconds from Lambda context or a safe default."""
    try:
        fn: Callable[[], int] = getattr(context, "get_remaining_time_in_millis")
        return int(fn())
    except Exception:
        return 8000
