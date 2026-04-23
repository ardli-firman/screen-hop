"""Display detection and display-selection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass
class DisplayInfo:
    """Lightweight normalized display object."""

    x: int
    y: int
    width: int
    height: int
    is_primary: bool
    name: str = ""


def _get_displays_from_screeninfo() -> List[Any]:
    """Read displays using `screeninfo` when available."""
    try:
        from screeninfo import get_monitors

        return list(get_monitors())
    except ImportError:
        return []
    except Exception:
        return []


def _get_displays_from_win32() -> List[DisplayInfo]:
    """Fallback display detection using Win32 APIs."""
    try:
        import win32api
        import win32con
    except ImportError:
        return []

    displays: List[DisplayInfo] = []
    try:
        enum_results = win32api.EnumDisplayMonitors(None, None)
    except Exception:
        return []

    for idx, item in enumerate(enum_results):
        try:
            hmonitor = item[0]
            info = win32api.GetMonitorInfo(hmonitor)
            left, top, right, bottom = info.get("Monitor", (0, 0, 0, 0))
            name = str(info.get("Device", f"DISPLAY{idx + 1}"))
            flags = int(info.get("Flags", 0))
            is_primary = bool(flags & win32con.MONITORINFOF_PRIMARY)
            displays.append(
                DisplayInfo(
                    x=int(left),
                    y=int(top),
                    width=max(0, int(right) - int(left)),
                    height=max(0, int(bottom) - int(top)),
                    is_primary=is_primary,
                    name=name,
                )
            )
        except Exception:
            continue

    return displays


def get_monitors() -> List[Any]:
    """Compatibility wrapper returning detected displays."""
    displays = _get_displays_from_screeninfo()
    if displays:
        return displays
    return _get_displays_from_win32()


def get_displays() -> List[Any]:
    """Return logical displays attached to the desktop."""
    return get_monitors()


def get_primary_display() -> Optional[Any]:
    for display in get_displays():
        if getattr(display, "is_primary", False):
            return display
    return None


def get_primary_monitor() -> Optional[Any]:
    """Backward-compatible alias for old monitor naming."""
    return get_primary_display()


def get_extended_displays() -> List[Any]:
    """Return non-primary displays (targets when using Extend mode)."""
    displays = get_displays()
    if not displays:
        return []

    primary_count = sum(1 for d in displays if getattr(d, "is_primary", False))
    if primary_count == 1:
        targets = [d for d in displays if not getattr(d, "is_primary", False)]
        if targets:
            return targets

    # Fallback for drivers/libs that do not set primary flag reliably.
    if len(displays) > 1:
        return displays[1:]
    return []


def get_external_monitors() -> List[Any]:
    """Backward-compatible alias for old monitor naming."""
    return get_extended_displays()


def has_multiple_displays() -> bool:
    """Check whether desktop is in logical multi-display mode."""
    return len(get_displays()) > 1


def select_external_monitor(monitors: List[Any]) -> Optional[Any]:
    """Backward-compatible helper for legacy callers."""
    if not monitors:
        return None
    return monitors[0]


def display_to_id(display: Any) -> str:
    """Build a stable display id from geometry and primary flag."""
    return (
        f"{getattr(display, 'x', 0)}:"
        f"{getattr(display, 'y', 0)}:"
        f"{getattr(display, 'width', 0)}:"
        f"{getattr(display, 'height', 0)}:"
        f"{1 if getattr(display, 'is_primary', False) else 0}"
    )


def monitor_to_id(monitor: Any) -> str:
    """Backward-compatible alias for old monitor naming."""
    return display_to_id(monitor)


def get_display_name(display: Any, index: int) -> str:
    """Build a human-readable display label for UI."""
    name = str(getattr(display, "name", "") or "").strip()
    width = getattr(display, "width", 0)
    height = getattr(display, "height", 0)
    role = "Primary" if getattr(display, "is_primary", False) else "Secondary"

    if name:
        return f"Display {index + 1} ({name}) - {width}x{height} [{role}]"
    return f"Display {index + 1} - {width}x{height} [{role}]"


def get_monitor_display_name(monitor: Any, index: int) -> str:
    """Backward-compatible alias for old monitor naming."""
    return get_display_name(monitor, index)


def get_display_choices() -> List[Tuple[str, str]]:
    """Return available target displays as list of (display_id, display_name)."""
    all_displays = get_displays()
    if not all_displays:
        return []

    choices: List[Tuple[str, str]] = []
    for idx, display in enumerate(all_displays):
        choices.append((display_to_id(display), get_display_name(display, idx)))
    return choices


def get_monitor_choices() -> List[Tuple[str, str]]:
    """Backward-compatible alias for old monitor naming."""
    return get_display_choices()


def find_display_by_id(
    display_id: str | None, displays: List[Any] | None = None
) -> Optional[Any]:
    """Find display object from a saved display id."""
    if not display_id:
        return None

    search_scope = displays if displays is not None else get_displays()
    for display in search_scope:
        if display_to_id(display) == display_id:
            return display
    return None


def find_monitor_by_id(monitor_id: str | None, monitors: List[Any] | None = None) -> Optional[Any]:
    """Backward-compatible alias for old monitor naming."""
    return find_display_by_id(monitor_id, displays=monitors)


def resolve_display_for_preset(preset: dict) -> Tuple[Optional[Any], str, bool]:
    """Resolve display target for a preset.

    Returns:
        Tuple of (display, display_name, used_fallback)
    """
    displays = get_displays()
    if not displays:
        return None, "", False

    saved_display_id = preset.get("display_id") or preset.get("monitor_id")
    selected = find_display_by_id(saved_display_id, displays=displays)
    all_displays = get_displays()
    if selected:
        try:
            idx = all_displays.index(selected)
        except ValueError:
            idx = 0
        return selected, get_display_name(selected, idx), False

    fallback = get_primary_display() or displays[0]
    try:
        idx = all_displays.index(fallback)
    except ValueError:
        idx = 0
    return fallback, get_display_name(fallback, idx), True


def resolve_monitor_for_preset(preset: dict) -> Tuple[Optional[Any], str, bool]:
    """Backward-compatible alias for old monitor naming."""
    return resolve_display_for_preset(preset)
