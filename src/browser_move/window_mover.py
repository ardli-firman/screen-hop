"""Window finding and moving functionality for browser windows.

Uses win32gui to locate browser windows by class name with retry logic
for handling browser startup delays.
"""

import time
from typing import Any

import win32con
import win32gui

from src.browser_move.monitors import get_external_monitors

# Window positioning constants
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_SHOW = 5


def find_browser_window(browser_type: str, timeout: float = 10.0) -> int | None:
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

    Returns:
        The window handle (hwnd) as an integer if found, None otherwise.

    Example:
        >>> hwnd = find_browser_window("firefox")
        >>> if hwnd:
        ...     print(f"Found Firefox window: {hwnd}")
        ... else:
        ...     print("Firefox window not found")
    """
    browser_type = browser_type.lower().strip()

    if browser_type == "firefox":
        target_class = "MozillaWindowClass"
    elif browser_type in ("chrome", "edge"):
        target_class = "Chrome_WidgetWin_"
    else:
        return None

    hwnds: list[int] = []

    def callback(hwnd: int, extra: None) -> bool:
        if win32gui.IsWindowVisible(hwnd):
            class_name = win32gui.GetClassName(hwnd)
            if class_name and target_class in class_name:
                hwnds.append(hwnd)
        return True

    start_time = time.time()
    delay = 0.5

    while time.time() - start_time < timeout:
        hwnds.clear()
        win32gui.EnumWindows(callback, None)
        if hwnds:
            return hwnds[0]
        time.sleep(delay)
        delay = min(delay * 2, 2.0)

    return None


def move_window_to_monitor(hwnd: int, monitor: Any) -> bool:
    try:
        if win32gui.IsZoomed(hwnd):
            win32gui.ShowWindow(hwnd, SW_RESTORE)

        x, y = monitor.x, monitor.y
        w, h = monitor.width, monitor.height
        flags = SWP_NOZORDER | SWP_NOACTIVATE
        win32gui.SetWindowPos(hwnd, 0, x, y, w, h, flags)

        win32gui.ShowWindow(hwnd, SW_MAXIMIZE)

        return True
    except Exception:
        return False


def move_browser_to_external(browser_type: str) -> bool:
    monitors = get_external_monitors()
    if not monitors:
        return False

    hwnd = find_browser_window(browser_type)
    if not hwnd:
        return False

    return move_window_to_monitor(hwnd, monitors[0])
