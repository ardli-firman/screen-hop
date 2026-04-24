"""Preset execution pipeline for ScreenHop."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

from src.browser_move.config import get_preset_programs
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


def _program_label(program: dict, index: int) -> str:
    label = str(program.get("label") or "").strip()
    if label:
        return label

    executable_path = str(program.get("executable_path") or "").strip()
    if executable_path:
        return Path(executable_path).stem or f"Program {index}"
    return f"Program {index}"


def _execute_program(
    program: dict,
    preset_name: str,
    index: int,
    total: int,
    reporter: StatusReporter | None,
    timeout: float,
) -> bool:
    executable_path = str(program.get("executable_path") or "").strip()
    launch_args = str(program.get("launch_args") or "").strip()
    working_directory = str(program.get("working_directory") or "").strip()
    title_hint = str(program.get("window_title_hint") or "").strip()
    app_label = _program_label(program, index)
    progress = f"{index}/{total}"

    target_display, target_label, used_fallback = resolve_display_for_preset(program)
    if not target_display:
        _emit(
            reporter,
            "error",
            f"{preset_name} [{progress}] {app_label}: no display detected on the Windows desktop.",
        )
        return False

    if used_fallback:
        _emit(
            reporter,
            "running",
            f"{preset_name} [{progress}] saved display not found. Using {target_label} for {app_label}.",
        )
    else:
        _emit(
            reporter,
            "running",
            f"{preset_name} [{progress}] launching {app_label} on {target_label}...",
        )

    existing_hwnds = snapshot_visible_window_handles()
    process = launch_executable(executable_path, launch_args, working_directory)
    if not process:
        _emit(
            reporter,
            "error",
            f"{preset_name} [{progress}] {app_label}: executable path is invalid or the app could not be launched.",
        )
        return False

    _emit(reporter, "running", f"{preset_name} [{progress}] waiting for {app_label} window...")
    hwnd = find_launched_window(
        process_id=getattr(process, "pid", None),
        existing_hwnds=existing_hwnds,
        window_title_hint=title_hint,
        timeout=timeout,
    )
    if not hwnd:
        _emit(
            reporter,
            "error",
            f"{preset_name} [{progress}] {app_label}: launched app window was not found.",
        )
        return False

    moved = move_window_to_monitor(hwnd, target_display)
    if not moved:
        _emit(
            reporter,
            "error",
            f"{preset_name} [{progress}] {app_label}: window was found but could not be moved to {target_label}.",
        )
        return False

    suffix = f" ({launch_args})" if launch_args else ""
    _emit(reporter, "ready", f"{preset_name} [{progress}] {app_label} moved to {target_label}{suffix}")
    return True


def execute_preset(
    preset: dict,
    reporter: StatusReporter | None = None,
    timeout: float = 10.0,
) -> bool:
    """Launch every preset program and move each window to its target display."""
    preset_name = str(preset.get("name") or "Preset").strip() or "Preset"
    programs = get_preset_programs(preset)
    total = len(programs)
    if total == 0:
        _emit(reporter, "error", f"{preset_name} has no programs to run.")
        return False

    success_count = 0
    for index, program in enumerate(programs, start=1):
        if _execute_program(
            program,
            preset_name=preset_name,
            index=index,
            total=total,
            reporter=reporter,
            timeout=timeout,
        ):
            success_count += 1

    if success_count == total:
        noun = "program" if total == 1 else "programs"
        _emit(reporter, "ready", f"{preset_name}: all {total} {noun} launched and moved.")
        return True

    failed_count = total - success_count
    _emit(
        reporter,
        "error",
        (
            f"{preset_name}: {success_count}/{total} programs launched and moved; "
            f"{failed_count} failed."
        )
    )
    return False
