"""Preset execution pipeline for ScreenHop."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

from src.browser_move.launcher import launch_executable
from src.browser_move.monitors import resolve_display_for_preset
from src.browser_move.window_mover import (
    find_launched_window,
    move_window_to_monitor,
    snapshot_visible_window_handles,
)

StatusType = Literal["ready", "running", "error", "info"]
StatusReporter = Callable[[StatusType, str], None]


class PresetExecutionError(RuntimeError):
    """Raised when a preset cannot be executed."""


def _emit(reporter: StatusReporter | None, status_type: StatusType, message: str) -> None:
    if reporter:
        reporter(status_type, message)


def execute_preset(
    preset: dict,
    reporter: StatusReporter | None = None,
    timeout: float = 10.0,
) -> bool:
    """Launch the preset application and move its window to the target display."""
    preset_name = str(preset.get("name") or "Preset").strip() or "Preset"
    executable_path = str(preset.get("executable_path") or "").strip()
    launch_args = str(preset.get("launch_args") or "").strip()
    working_directory = str(preset.get("working_directory") or "").strip()
    title_hint = str(preset.get("window_title_hint") or "").strip()

    target_display, target_label, used_fallback = resolve_display_for_preset(preset)
    if not target_display:
        _emit(reporter, "error", "No display detected on the Windows desktop.")
        return False

    app_label = Path(executable_path).stem or preset_name
    if used_fallback:
        _emit(
            reporter,
            "running",
            f"Saved display not found. Using {target_label} for {app_label}.",
        )
    else:
        _emit(reporter, "running", f"Launching {app_label} on {target_label}...")

    existing_hwnds = snapshot_visible_window_handles()
    process = launch_executable(executable_path, launch_args, working_directory)
    if not process:
        _emit(reporter, "error", "Executable path is invalid or the app could not be launched.")
        return False

    _emit(reporter, "running", f"Waiting for {app_label} window...")
    hwnd = find_launched_window(
        process_id=getattr(process, "pid", None),
        existing_hwnds=existing_hwnds,
        window_title_hint=title_hint,
        timeout=timeout,
    )
    if not hwnd:
        _emit(reporter, "error", "Launched app window was not found. Check the window title hint or app behavior.")
        return False

    moved = move_window_to_monitor(hwnd, target_display)
    if not moved:
        _emit(reporter, "error", f"Window was found but could not be moved to {target_label}.")
        return False

    suffix = f" ({launch_args})" if launch_args else ""
    _emit(reporter, "ready", f"{preset_name} moved to {target_label}{suffix}")
    return True
