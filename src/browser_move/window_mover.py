"""Window finding and moving functionality for browser windows.

Uses win32gui to locate browser windows by class name with retry logic
for handling browser startup delays.
"""

from __future__ import annotations

import time
from typing import Any

import win32con
import win32gui

from src.browser_move.monitors import get_external_monitors

# Window positioning constants
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_SHOW = 5


def _target_window_class(browser_type: str) -> str | None:
    """Resolve browser type to top-level window class name pattern."""
    browser_type = browser_type.lower().strip()

    if browser_type == "firefox":
        return "MozillaWindowClass"
    if browser_type in ("chrome", "edge"):
        return "Chrome_WidgetWin_"
    return None


def list_browser_windows(browser_type: str) -> list[int]:
    """List visible top-level windows for a given browser type."""
    target_class = _target_window_class(browser_type)
    if not target_class:
        return []

    raw_candidates: list[tuple[int, int, bool]] = []

    def callback(hwnd: int, extra: None) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return True

        class_name = win32gui.GetClassName(hwnd)
        if class_name and target_class in class_name:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = max(0, right - left)
                height = max(0, bottom - top)
                area = width * height
            except Exception:
                area = 0

            title = str(win32gui.GetWindowText(hwnd) or "").strip()
            has_title = bool(title)
            raw_candidates.append((hwnd, area, has_title))
        return True

    win32gui.EnumWindows(callback, None)

    if not raw_candidates:
        return []

    # Prefer real browser windows over tiny helper/popup windows.
    filtered = [item for item in raw_candidates if item[1] >= 80_000]
    candidates = filtered if filtered else raw_candidates

    # Highest score first: has title + larger window area.
    candidates.sort(key=lambda item: ((1 if item[2] else 0) * 10_000_000 + item[1]), reverse=True)
    return [item[0] for item in candidates]


def find_browser_window(
    browser_type: str,
    timeout: float = 10.0,
    exclude_hwnds: set[int] | None = None,
) -> int | None:
    """Find a browser window by its class name.

    Uses EnumWindows to iterate through all windows and find the first
    visible window matching the browser's class name. Includes retry logic
    with exponential backoff to handle browser startup delays.

    Args:
        browser_type: The browser to find. Supported values:
            - "firefox": Looks for MozillaWindowClass
            - "chrome": Looks for Chrome_WidgetWin_*
            - "edge": Looks for Chrome_WidgetWin_*
        timeout: Maximum time in seconds to wait for the window.
            Defaults to 10.0 seconds.
        exclude_hwnds: Optional set of hwnds to ignore while searching.

    Returns:
        The window handle (hwnd) as an integer if found, None otherwise.

    Example:
        >>> hwnd = find_browser_window("firefox")
        >>> if hwnd:
        ...     print(f"Found Firefox window: {hwnd}")
        ... else:
        ...     print("Firefox window not found")
    """
    if not _target_window_class(browser_type):
        return None

    excluded = exclude_hwnds or set()

    start_time = time.time()
    delay = 0.5

    while time.time() - start_time < timeout:
        hwnds = [hwnd for hwnd in list_browser_windows(browser_type) if hwnd not in excluded]
        if hwnds:
            return hwnds[0]
        time.sleep(delay)
        delay = min(delay * 2, 2.0)

    return None


def _window_center_in_monitor(hwnd: int, monitor: Any) -> bool:
    """Check whether window center point is within monitor bounds."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    cx = (left + right) // 2
    cy = (top + bottom) // 2

    mx = int(getattr(monitor, "x", 0))
    my = int(getattr(monitor, "y", 0))
    mw = int(getattr(monitor, "width", 0))
    mh = int(getattr(monitor, "height", 0))

    return mx <= cx < (mx + mw) and my <= cy < (my + mh)


def _get_window_show_cmd(hwnd: int) -> int | None:
    """Get Win32 show command from window placement, if available."""
    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        if isinstance(placement, tuple) and len(placement) >= 2:
            return int(placement[1])
    except Exception:
        return None
    return None


def _is_window_minimized(hwnd: int) -> bool:
    """Compatibility-safe minimized check."""
    show_cmd = _get_window_show_cmd(hwnd)
    if show_cmd is None:
        return False

    minimized_states = {
        int(getattr(win32con, "SW_SHOWMINIMIZED", 2)),
        int(getattr(win32con, "SW_MINIMIZE", 6)),
        int(getattr(win32con, "SW_SHOWMINNOACTIVE", 7)),
        int(getattr(win32con, "SW_FORCEMINIMIZE", 11)),
    }
    return show_cmd in minimized_states


def _is_window_maximized(hwnd: int) -> bool:
    """Compatibility-safe maximized check."""
    show_cmd = _get_window_show_cmd(hwnd)
    if show_cmd is None:
        return False

    maximized_states = {
        int(getattr(win32con, "SW_SHOWMAXIMIZED", 3)),
        int(getattr(win32con, "SW_MAXIMIZE", 3)),
    }
    return show_cmd in maximized_states


def _window_overlaps_monitor(hwnd: int, monitor: Any, min_overlap_ratio: float = 0.4) -> bool:
    """Check whether enough of the window overlaps the monitor area."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    ww = max(0, right - left)
    wh = max(0, bottom - top)
    window_area = ww * wh
    if window_area <= 0:
        return False

    mx = int(getattr(monitor, "x", 0))
    my = int(getattr(monitor, "y", 0))
    mw = int(getattr(monitor, "width", 0))
    mh = int(getattr(monitor, "height", 0))

    il = max(left, mx)
    it = max(top, my)
    ir = min(right, mx + mw)
    ib = min(bottom, my + mh)
    iw = max(0, ir - il)
    ih = max(0, ib - it)
    intersection_area = iw * ih

    return (intersection_area / window_area) >= min_overlap_ratio


def move_window_to_monitor(hwnd: int, monitor: Any) -> bool:
    """Move window to a target monitor and verify final placement."""
    try:
        if _is_window_minimized(hwnd) or _is_window_maximized(hwnd):
            win32gui.ShowWindow(hwnd, SW_RESTORE)

        x, y = monitor.x, monitor.y
        w, h = monitor.width, monitor.height
        flags = SWP_NOZORDER | SWP_NOACTIVATE | SWP_SHOWWINDOW

        # Try multiple movement methods and retry because some browsers
        # re-apply fullscreen/maximized state shortly after launch.
        for _ in range(8):
            win32gui.SetWindowPos(hwnd, 0, x, y, w, h, flags)
            time.sleep(0.12)
            if _window_center_in_monitor(hwnd, monitor) or _window_overlaps_monitor(hwnd, monitor):
                return True

            win32gui.MoveWindow(hwnd, int(x), int(y), int(w), int(h), True)
            time.sleep(0.12)
            if _window_center_in_monitor(hwnd, monitor) or _window_overlaps_monitor(hwnd, monitor):
                return True

            win32gui.ShowWindow(hwnd, SW_MAXIMIZE)
            time.sleep(0.12)
            if _window_center_in_monitor(hwnd, monitor) or _window_overlaps_monitor(hwnd, monitor):
                return True

        try:
            rect = win32gui.GetWindowRect(hwnd)
            print(f"[window_mover] Failed to verify move. hwnd={hwnd}, rect={rect}, target=({x},{y},{w},{h})")
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"[window_mover] move_window_to_monitor error: {e}")
        return False


def move_browser_to_external(browser_type: str) -> bool:
    monitors = get_external_monitors()
    if not monitors:
        return False

    hwnd = find_browser_window(browser_type)
    if not hwnd:
        return False

    return move_window_to_monitor(hwnd, monitors[0])
