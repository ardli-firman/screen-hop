"""Window discovery and monitor movement helpers for ScreenHop."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

try:
    import win32con
    import win32gui
    import win32process
except ImportError:
    win32con = None
    win32gui = None
    win32process = None

# Window positioning constants
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SW_RESTORE = 9
SW_MAXIMIZE = 3


@dataclass(frozen=True)
class WindowCandidate:
    """Lightweight snapshot of a visible top-level window."""

    hwnd: int
    title: str
    class_name: str
    area: int
    pid: int


def _win32_ready() -> bool:
    return bool(win32gui and win32process)


def _safe_window_area(hwnd: int) -> int:
    if not _win32_ready():
        return 0
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = max(0, right - left)
        height = max(0, bottom - top)
        return width * height
    except Exception:
        return 0


def _safe_window_pid(hwnd: int) -> int:
    if not _win32_ready():
        return 0
    try:
        _thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
        return int(pid)
    except Exception:
        return 0


def list_visible_windows() -> list[WindowCandidate]:
    """Return visible top-level windows as ranked candidates."""
    if not _win32_ready():
        return []

    candidates: list[WindowCandidate] = []

    def callback(hwnd: int, _extra: None) -> bool:
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True

            area = _safe_window_area(hwnd)
            if area <= 0:
                return True

            title = str(win32gui.GetWindowText(hwnd) or "").strip()
            class_name = str(win32gui.GetClassName(hwnd) or "").strip()
            candidates.append(
                WindowCandidate(
                    hwnd=hwnd,
                    title=title,
                    class_name=class_name,
                    area=area,
                    pid=_safe_window_pid(hwnd),
                )
            )
        except Exception:
            return True
        return True

    win32gui.EnumWindows(callback, None)
    candidates.sort(key=lambda item: ((1 if item.title else 0), item.area), reverse=True)
    return candidates


def snapshot_visible_window_handles() -> set[int]:
    return {candidate.hwnd for candidate in list_visible_windows()}


def choose_window_candidate(
    candidates: Iterable[WindowCandidate],
    process_id: int | None = None,
    window_title_hint: str | None = None,
) -> WindowCandidate | None:
    """Choose the best candidate using PID, title hint, then area fallback."""
    window_list = list(candidates)
    if not window_list:
        return None

    ranked = sorted(
        window_list,
        key=lambda item: (item.area, (1 if item.title else 0)),
        reverse=True,
    )

    if process_id:
        process_matches = [item for item in ranked if item.pid == process_id]
        if process_matches:
            return process_matches[0]

    title_hint = str(window_title_hint or "").strip().lower()
    if title_hint:
        hint_matches = [item for item in ranked if title_hint in item.title.lower()]
        if hint_matches:
            return hint_matches[0]

    return ranked[0]


def find_launched_window(
    process_id: int | None,
    existing_hwnds: set[int] | None = None,
    window_title_hint: str | None = None,
    timeout: float = 10.0,
) -> int | None:
    """Poll for a newly created visible window after launching an app."""
    if not _win32_ready():
        return None

    baseline = existing_hwnds or set()
    start_time = time.time()
    delay = 0.25

    while time.time() - start_time < timeout:
        current_windows = [item for item in list_visible_windows() if item.hwnd not in baseline]
        chosen = choose_window_candidate(
            current_windows,
            process_id=process_id,
            window_title_hint=window_title_hint,
        )
        if chosen:
            return chosen.hwnd

        time.sleep(delay)
        delay = min(delay * 1.6, 1.5)

    return None


def _window_center_in_monitor(hwnd: int, monitor: Any) -> bool:
    if not _win32_ready():
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    cx = (left + right) // 2
    cy = (top + bottom) // 2

    mx = int(getattr(monitor, "x", 0))
    my = int(getattr(monitor, "y", 0))
    mw = int(getattr(monitor, "width", 0))
    mh = int(getattr(monitor, "height", 0))

    return mx <= cx < (mx + mw) and my <= cy < (my + mh)


def _get_window_show_cmd(hwnd: int) -> int | None:
    if not _win32_ready():
        return None

    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        if isinstance(placement, tuple) and len(placement) >= 2:
            return int(placement[1])
    except Exception:
        return None
    return None


def _is_window_minimized(hwnd: int) -> bool:
    show_cmd = _get_window_show_cmd(hwnd)
    if show_cmd is None or not win32con:
        return False

    minimized_states = {
        int(getattr(win32con, "SW_SHOWMINIMIZED", 2)),
        int(getattr(win32con, "SW_MINIMIZE", 6)),
        int(getattr(win32con, "SW_SHOWMINNOACTIVE", 7)),
        int(getattr(win32con, "SW_FORCEMINIMIZE", 11)),
    }
    return show_cmd in minimized_states


def _is_window_maximized(hwnd: int) -> bool:
    show_cmd = _get_window_show_cmd(hwnd)
    if show_cmd is None or not win32con:
        return False

    maximized_states = {
        int(getattr(win32con, "SW_SHOWMAXIMIZED", 3)),
        int(getattr(win32con, "SW_MAXIMIZE", 3)),
    }
    return show_cmd in maximized_states


def _window_overlaps_monitor(hwnd: int, monitor: Any, min_overlap_ratio: float = 0.4) -> bool:
    if not _win32_ready():
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    window_width = max(0, right - left)
    window_height = max(0, bottom - top)
    window_area = window_width * window_height
    if window_area <= 0:
        return False

    mx = int(getattr(monitor, "x", 0))
    my = int(getattr(monitor, "y", 0))
    mw = int(getattr(monitor, "width", 0))
    mh = int(getattr(monitor, "height", 0))

    intersection_left = max(left, mx)
    intersection_top = max(top, my)
    intersection_right = min(right, mx + mw)
    intersection_bottom = min(bottom, my + mh)
    intersection_width = max(0, intersection_right - intersection_left)
    intersection_height = max(0, intersection_bottom - intersection_top)
    intersection_area = intersection_width * intersection_height

    return (intersection_area / window_area) >= min_overlap_ratio


def move_window_to_monitor(hwnd: int, monitor: Any) -> bool:
    """Move a window to a target monitor and verify final placement."""
    if not _win32_ready():
        return False

    try:
        if _is_window_minimized(hwnd) or _is_window_maximized(hwnd):
            win32gui.ShowWindow(hwnd, SW_RESTORE)

        x, y = int(getattr(monitor, "x", 0)), int(getattr(monitor, "y", 0))
        width, height = int(getattr(monitor, "width", 0)), int(getattr(monitor, "height", 0))
        flags = SWP_NOZORDER | SWP_NOACTIVATE | SWP_SHOWWINDOW

        for _ in range(8):
            win32gui.SetWindowPos(hwnd, 0, x, y, width, height, flags)
            time.sleep(0.12)
            if _window_center_in_monitor(hwnd, monitor) or _window_overlaps_monitor(hwnd, monitor):
                return True

            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            time.sleep(0.12)
            if _window_center_in_monitor(hwnd, monitor) or _window_overlaps_monitor(hwnd, monitor):
                return True

            win32gui.ShowWindow(hwnd, SW_MAXIMIZE)
            time.sleep(0.12)
            if _window_center_in_monitor(hwnd, monitor) or _window_overlaps_monitor(hwnd, monitor):
                return True

        try:
            rect = win32gui.GetWindowRect(hwnd)
            print(
                f"[window_mover] Failed to verify move. hwnd={hwnd}, rect={rect}, target=({x},{y},{width},{height})"
            )
        except Exception:
            pass
        return False
    except Exception as exc:
        print(f"[window_mover] move_window_to_monitor error: {exc}")
        return False
