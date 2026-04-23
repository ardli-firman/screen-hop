"""Desktop and startup shortcuts for browser move automation.

This module provides functions to create desktop shortcuts and manage
startup folder shortcuts for the browser move automation application.
"""

import sys
from pathlib import Path

from win32com.client import Dispatch
import winshell


def get_desktop_path() -> Path:
    """Get the user's desktop path.

    Returns:
        Path to the desktop folder.
    """
    return Path(winshell.desktop())


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

    # Development mode - use pythonw with -m browser_move.main
    # Find pythonw.exe
    python_dir = Path(sys.executable).parent
    pythonw_path = python_dir / "pythonw.exe"

    if not pythonw_path.exists():
        # Fallback to python.exe if pythonw doesn't exist
        pythonw_path = Path(sys.executable)

    args = "-m browser_move.main"
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
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))

        target, args = _get_target_and_args(preset_name)
        shortcut.Targetpath = target

        if args:
            shortcut.Arguments = args

        shortcut.WorkingDirectory = _get_working_directory()

        icon_path = _get_icon_path()
        if icon_path:
            shortcut.IconLocation = icon_path

        shortcut.save()
        return True

    except Exception:
        return False


def create_desktop_shortcut(preset_name: str | None = None) -> bool:
    """Create a desktop shortcut for browser move automation.

    Args:
        preset_name: Optional preset name to include in shortcut name and arguments.

    Returns:
        True if shortcut was created successfully, False otherwise.
    """
    try:
        desktop = get_desktop_path()

        # Create shortcut name
        if preset_name:
            shortcut_name = f"BrowserMove - {preset_name}.lnk"
        else:
            shortcut_name = "BrowserMove.lnk"

        shortcut_path = desktop / shortcut_name

        return create_shortcut(shortcut_path, preset_name)

    except Exception:
        return False


def is_in_startup(preset_name: str | None = None) -> bool:
    """Check if a shortcut exists in the startup folder.

    Args:
        preset_name: Optional preset name to check for specific preset shortcut.

    Returns:
        True if shortcut exists in startup folder.
    """
    startup = get_startup_path()

    if preset_name:
        shortcut_name = f"BrowserMove - {preset_name}.lnk"
    else:
        shortcut_name = "BrowserMove.lnk"

    shortcut_path = startup / shortcut_name
    return shortcut_path.exists()


def add_to_startup(preset_name: str | None = None) -> bool:
    """Add a shortcut to the Windows startup folder.

    Args:
        preset_name: Optional preset name to include in shortcut.

    Returns:
        True if shortcut was added successfully, False otherwise.
    """
    try:
        startup = get_startup_path()

        if preset_name:
            shortcut_name = f"BrowserMove - {preset_name}.lnk"
        else:
            shortcut_name = "BrowserMove.lnk"

        shortcut_path = startup / shortcut_name

        return create_shortcut(shortcut_path, preset_name)

    except Exception:
        return False


def remove_from_startup(preset_name: str | None = None) -> bool:
    """Remove a shortcut from the Windows startup folder.

    Args:
        preset_name: Optional preset name for specific preset shortcut.

    Returns:
        True if shortcut was removed or didn't exist, False on error.
    """
    try:
        startup = get_startup_path()

        if preset_name:
            shortcut_name = f"BrowserMove - {preset_name}.lnk"
        else:
            shortcut_name = "BrowserMove.lnk"

        shortcut_path = startup / shortcut_name

        if shortcut_path.exists():
            shortcut_path.unlink()

        return True

    except Exception:
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
    """Get all BrowserMove shortcuts in the startup folder.

    Returns:
        List of paths to BrowserMove shortcuts in startup folder.
    """
    startup = get_startup_path()
    shortcuts = []

    for item in startup.iterdir():
        if item.name.startswith("BrowserMove") and item.suffix == ".lnk":
            shortcuts.append(item)

    return shortcuts


def remove_all_startup_shortcuts() -> int:
    """Remove all BrowserMove shortcuts from the startup folder.

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
