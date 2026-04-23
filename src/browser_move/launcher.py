"""Executable launch helpers for ScreenHop."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def normalize_executable_path(executable_path: str | None) -> str:
    return str(executable_path or "").strip()


def is_valid_executable_path(executable_path: str | None) -> bool:
    path_value = normalize_executable_path(executable_path)
    if not path_value:
        return False

    path = Path(path_value)
    return path.exists() and path.is_file() and path.suffix.lower() == ".exe"


def build_command_line(executable_path: str, launch_args: str | None = None) -> str:
    """Build a Windows command line for CreateProcess."""
    normalized_path = normalize_executable_path(executable_path)
    command_line = subprocess.list2cmdline([normalized_path])
    args_text = str(launch_args or "").strip()
    if args_text:
        command_line = f"{command_line} {args_text}"
    return command_line


def resolve_working_directory(
    executable_path: str,
    working_directory: str | None = None,
) -> str:
    configured = str(working_directory or "").strip()
    if configured:
        return configured
    return str(Path(executable_path).expanduser().resolve().parent)


def launch_executable(
    executable_path: str,
    launch_args: str | None = None,
    working_directory: str | None = None,
) -> subprocess.Popen | None:
    """Launch an executable and return the spawned process."""
    normalized_path = normalize_executable_path(executable_path)
    if not is_valid_executable_path(normalized_path):
        return None

    cwd = resolve_working_directory(normalized_path, working_directory)
    if cwd and not os.path.isdir(cwd):
        return None

    command_line = build_command_line(normalized_path, launch_args)

    try:
        return subprocess.Popen(command_line, cwd=cwd or None)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"[launcher] Failed to launch '{normalized_path}': {exc}")
        return None
