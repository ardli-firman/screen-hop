"""Monitor detection and monitor-selection helpers."""

from typing import List, Optional, Any, Tuple


def get_monitors() -> List[Any]:
    try:
        from screeninfo import get_monitors

        return list(get_monitors())
    except ImportError:
        return []


def get_primary_monitor() -> Optional[Any]:
    for m in get_monitors():
        if m.is_primary:
            return m
    return None


def get_external_monitors() -> List[Any]:
    return [m for m in get_monitors() if not m.is_primary]


def select_external_monitor(monitors: List[Any]) -> Optional[Any]:
    if not monitors:
        return None
    return monitors[0]


def monitor_to_id(monitor: Any) -> str:
    """Build a stable monitor id from geometry and primary flag."""
    return (
        f"{getattr(monitor, 'x', 0)}:"
        f"{getattr(monitor, 'y', 0)}:"
        f"{getattr(monitor, 'width', 0)}:"
        f"{getattr(monitor, 'height', 0)}:"
        f"{1 if getattr(monitor, 'is_primary', False) else 0}"
    )


def get_monitor_display_name(monitor: Any, index: int) -> str:
    """Build a human-readable monitor label for UI."""
    name = str(getattr(monitor, "name", "") or "").strip()
    width = getattr(monitor, "width", 0)
    height = getattr(monitor, "height", 0)
    role = "Primary" if getattr(monitor, "is_primary", False) else "Secondary"

    if name:
        return f"Monitor {index + 1} ({name}) - {width}x{height} [{role}]"
    return f"Monitor {index + 1} - {width}x{height} [{role}]"


def get_monitor_choices() -> List[Tuple[str, str]]:
    """Return monitor choices as list of (monitor_id, display_name)."""
    choices: List[Tuple[str, str]] = []
    for idx, monitor in enumerate(get_monitors()):
        choices.append((monitor_to_id(monitor), get_monitor_display_name(monitor, idx)))
    return choices


def find_monitor_by_id(monitor_id: str | None) -> Optional[Any]:
    """Find monitor object from saved monitor id."""
    if not monitor_id:
        return None

    for monitor in get_monitors():
        if monitor_to_id(monitor) == monitor_id:
            return monitor
    return None


def resolve_monitor_for_preset(preset: dict) -> Tuple[Optional[Any], str, bool]:
    """Resolve monitor target for a preset.

    Returns:
        Tuple of (monitor, display_name, used_fallback)
    """
    monitors = get_monitors()
    if not monitors:
        return None, "", False

    selected = find_monitor_by_id(preset.get("monitor_id"))
    if selected:
        try:
            idx = monitors.index(selected)
        except ValueError:
            idx = 0
        return selected, get_monitor_display_name(selected, idx), False

    fallback = get_primary_monitor() or monitors[0]
    try:
        idx = monitors.index(fallback)
    except ValueError:
        idx = 0
    return fallback, get_monitor_display_name(fallback, idx), True
