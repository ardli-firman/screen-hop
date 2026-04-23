"""Desktop and startup shortcuts for ScreenHop.

This module provides functions to create desktop shortcuts and manage
startup folder shortcuts for the ScreenHop application.
"""

from __future__ import annotations

import sys
from pathlib import Path

from win32com.client import Dispatch
import winshell

from src.browser_move import APP_NAME


def _get_shortcut_name(preset_name: str | None = None) -> str:
    """Build shortcut filename for app or preset."""
    if preset_name:
        return f"{APP_NAME} - {preset_name}.lnk"
    return f"{APP_NAME}.lnk"


def get_desktop_path() -> Path:
    """Get the user's desktop path.

    Returns:
        Path to the desktop folder.
    """
    return Path(winshell.desktop())


def get_all_desktop_shortcuts() -> list[Path]:
    """Get all ScreenHop shortcuts on the desktop."""
    try:
        desktop = get_desktop_path()
        shortcuts = []

        for item in desktop.iterdir():
            if item.name.startswith(APP_NAME) and item.suffix.lower() == ".lnk":
                shortcuts.append(item)

        return shortcuts
    except Exception as exc:
        print(f"[shortcuts] Failed to enumerate desktop shortcuts: {exc}")
        return []


def get_startup_path() -> Path:
    """Get the Windows startup folder path.

    Returns:
        Path to the startup folder.
    """
    return Path(winshell.folder("startup"))


def _get_target_and_args(preset_name: str | None = None) -> tuple[str, str]:
    """Get shortcut target path and arguments.

    Determines whether to use the compiled exe or pythonw for development.

    Args:
        preset_name: Optional preset name to pass as argument.

    Returns:
        Tuple of (target_path, arguments).
    """
    # Check if running as compiled exe
    if getattr(sys, "frozen", False):
        # Running as compiled exe (PyInstaller)
        exe_path = Path(sys.executable)
        args = ""
        if preset_name:
            args = f'--preset "{preset_name}"'
        return str(exe_path), args

    # Development mode - use pythonw with the repo module entry point.
    # Find pythonw.exe
    python_dir = Path(sys.executable).parent
    pythonw_path = python_dir / "pythonw.exe"

    if not pythonw_path.exists():
        # Fallback to python.exe if pythonw doesn't exist
        pythonw_path = Path(sys.executable)

    args = "-m src.browser_move.main"
    if preset_name:
        args += f' --preset "{preset_name}"'

    return str(pythonw_path), args


def _get_working_directory() -> str:
    """Get the working directory for shortcuts.

    Returns:
        Working directory path as string.
    """
    if getattr(sys, "frozen", False):
        # For compiled exe, use exe directory
        return str(Path(sys.executable).parent)
    else:
        # For development, use project root
        return str(Path(__file__).parent.parent.parent)


def _get_icon_path() -> str | None:
    """Get the icon path for shortcuts.

    Returns:
        Icon path as string, or None if not found.
    """
    if getattr(sys, "frozen", False):
        # For compiled exe, the icon is embedded
        return str(Path(sys.executable))

    # For development, look for icon.ico in project root
    project_root = Path(__file__).parent.parent.parent
    icon_path = project_root / "icon.ico"

    if icon_path.exists():
        return str(icon_path)

    return None


def create_shortcut(shortcut_path: Path, preset_name: str | None = None) -> bool:
    """Create a Windows shortcut (.lnk file).

    Args:
        shortcut_path: Full path for the .lnk file.
        preset_name: Optional preset name to pass as argument.

    Returns:
        True if shortcut was created successfully, False otherwise.
    """
    try:
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))

        target, args = _get_target_and_args(preset_name)
        shortcut.TargetPath = target

        if args:
            shortcut.Arguments = args

        shortcut.WorkingDirectory = _get_working_directory()

        icon_path = _get_icon_path()
        if icon_path:
            shortcut.IconLocation = f"{icon_path},0"

        shortcut.Save()
        return True

    except Exception as exc:
        print(f"[shortcuts] Failed to create shortcut at '{shortcut_path}': {exc}")
        return False


def create_desktop_shortcut(preset_name: str | None = None) -> bool:
    """Create a desktop shortcut for ScreenHop.

    Args:
        preset_name: Optional preset name to include in shortcut name and arguments.

    Returns:
        True if shortcut was created successfully, False otherwise.
    """
    try:
        desktop = get_desktop_path()
        shortcut_path = desktop / _get_shortcut_name(preset_name)
        return create_shortcut(shortcut_path, preset_name)

    except Exception as exc:
        print(f"[shortcuts] Failed to create desktop shortcut: {exc}")
        return False


def ensure_single_desktop_shortcut(preset_name: str) -> bool:
    """Ensure desktop has only one ScreenHop shortcut for the given preset.

    Removes other ScreenHop desktop shortcuts and creates/updates the selected one.
    """
    if not preset_name:
        return False

    target_name = _get_shortcut_name(preset_name)
    target_path = get_desktop_path() / target_name

    for shortcut in get_all_desktop_shortcuts():
        if shortcut.name == target_name:
            continue
        try:
            shortcut.unlink()
        except Exception as exc:
            print(f"[shortcuts] Failed to remove desktop shortcut '{shortcut}': {exc}")
            return False

    return create_shortcut(target_path, preset_name)


def is_in_startup(preset_name: str | None = None) -> bool:
    """Check if a shortcut exists in the startup folder.

    Args:
        preset_name: Optional preset name to check for specific preset shortcut.

    Returns:
        True if shortcut exists in startup folder.
    """
    try:
        startup = get_startup_path()
        shortcut_path = startup / _get_shortcut_name(preset_name)
        return shortcut_path.exists()
    except Exception as exc:
        print(f"[shortcuts] Failed to check startup shortcut: {exc}")
        return False


def add_to_startup(preset_name: str | None = None) -> bool:
    """Add a shortcut to the Windows startup folder.

    Args:
        preset_name: Optional preset name to include in shortcut.

    Returns:
        True if shortcut was added successfully, False otherwise.
    """
    try:
        startup = get_startup_path()
        shortcut_path = startup / _get_shortcut_name(preset_name)
        return create_shortcut(shortcut_path, preset_name)

    except Exception as exc:
        print(f"[shortcuts] Failed to add startup shortcut: {exc}")
        return False


def ensure_single_startup_shortcut(preset_name: str) -> bool:
    """Ensure startup has only one ScreenHop shortcut for the given preset.

    Removes other ScreenHop startup shortcuts and creates/updates the selected one.
    """
    if not preset_name:
        return False

    target_name = _get_shortcut_name(preset_name)
    target_path = get_startup_path() / target_name

    for shortcut in get_all_startup_shortcuts():
        if shortcut.name == target_name:
            continue
        try:
            shortcut.unlink()
        except Exception as exc:
            print(f"[shortcuts] Failed to remove startup shortcut '{shortcut}': {exc}")
            return False

    return create_shortcut(target_path, preset_name)


def remove_from_startup(preset_name: str | None = None) -> bool:
    """Remove a shortcut from the Windows startup folder.

    Args:
        preset_name: Optional preset name for specific preset shortcut.

    Returns:
        True if shortcut was removed or didn't exist, False on error.
    """
    try:
        startup = get_startup_path()
        shortcut_path = startup / _get_shortcut_name(preset_name)

        if shortcut_path.exists():
            shortcut_path.unlink()

        return True

    except Exception as exc:
        print(f"[shortcuts] Failed to remove startup shortcut: {exc}")
        return False


def toggle_startup(preset_name: str | None = None) -> bool:
    """Toggle startup shortcut presence.

    If shortcut exists, remove it. If not, add it.

    Args:
        preset_name: Optional preset name for specific preset shortcut.

    Returns:
        True if operation was successful, False otherwise.
    """
    if is_in_startup(preset_name):
        return remove_from_startup(preset_name)
    else:
        return add_to_startup(preset_name)


def get_all_startup_shortcuts() -> list[Path]:
    """Get all ScreenHop shortcuts in the startup folder.

    Returns:
        List of paths to ScreenHop shortcuts in startup folder.
    """
    try:
        startup = get_startup_path()
        shortcuts = []

        for item in startup.iterdir():
            if item.name.startswith(APP_NAME) and item.suffix == ".lnk":
                shortcuts.append(item)

        return shortcuts
    except Exception as exc:
        print(f"[shortcuts] Failed to enumerate startup shortcuts: {exc}")
        return []


def remove_all_startup_shortcuts() -> int:
    """Remove all ScreenHop shortcuts from the startup folder.

    Returns:
        Number of shortcuts removed.
    """
    shortcuts = get_all_startup_shortcuts()
    removed = 0

    for shortcut in shortcuts:
        try:
            shortcut.unlink()
            removed += 1
        except Exception:
            pass

    return removed
