"""Entry point for Browser Move Automation application."""

import argparse
import sys
import time

import customtkinter as ctk

from src.browser_move.dpi import setup_dpi_awareness
from src.browser_move.single_instance import (
    check_single_instance,
    show_already_running_message,
)
from src.browser_move.app import MainWindow
from src.browser_move.tray import TrayManager
from src.browser_move.config import load_config
from src.browser_move.browsers import launch_browser
from src.browser_move.window_mover import find_browser_window, move_window_to_monitor
from src.browser_move.monitors import get_external_monitors


def main() -> int:
    """Main entry point for Browser Move Automation.

    Returns:
        Exit code: 0 for success, 1 for error/already running
    """
    setup_dpi_awareness()

    if not check_single_instance():
        show_already_running_message()
        return 1

    parser = argparse.ArgumentParser(
        description="Browser Move Automation - Launch and move browsers to external monitor"
    )
    parser.add_argument(
        "--preset",
        type=str,
        help="Run preset by name directly (bypasses GUI)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in background mode (tray only, no GUI window)",
    )
    args = parser.parse_args()

    if args.preset:
        success = run_preset_direct(args.preset)
        if not args.headless:
            return 0 if success else 1

    config = load_config()

    if args.headless:
        run_headless()
        return 0

    run_gui()
    return 0


def run_preset_direct(preset_name: str) -> bool:
    """Execute preset directly without GUI.

    Args:
        preset_name: Name of preset to run

    Returns:
        True if successful, False otherwise
    """
    config = load_config()
    preset = find_preset_by_name(config, preset_name)

    if not preset:
        print(f"Preset '{preset_name}' not found")
        return False

    monitors = get_external_monitors()
    if not monitors:
        print("No external monitor detected")
        return False

    proc = launch_browser(
        preset["browser_type"],
        preset["url"],
        preset.get("kiosk_mode", False),
        preset.get("browser_path"),
    )

    if not proc:
        print("Failed to launch browser")
        return False

    hwnd = find_browser_window(preset["browser_type"])
    if hwnd:
        move_window_to_monitor(hwnd, monitors[0])
        print(f"Browser moved to external monitor")
        return True
    else:
        print("Failed to find browser window")
        return False


def find_preset_by_name(config: dict, name: str) -> dict | None:
    """Find preset by name in config.

    Args:
        config: Configuration dictionary
        name: Preset name to search for

    Returns:
        Preset dict if found, None otherwise
    """
    for preset in config.get("presets", []):
        if preset.get("name") == name:
            return preset
    return None


def run_gui() -> None:
    """Run in normal GUI mode with tray and window."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = MainWindow(root)

    callbacks = {
        "show_window": app.show_window,
        "run_preset": lambda preset: app.run_preset_by_name(preset.get("name")),
        "open_settings": app.open_settings,
        "exit_app": lambda: on_exit(root, app.tray),
    }

    tray = TrayManager(callbacks)
    app.tray = tray
    tray.start()

    try:
        root.mainloop()
    finally:
        tray.stop()


def on_exit(root: ctk.CTk, tray: TrayManager) -> None:
    """Handle application exit.

    Args:
        root: CTk root window
        tray: Tray manager instance
    """
    tray.stop()
    root.quit()


def run_headless() -> None:
    """Run in headless mode (tray only, no GUI)."""
    callbacks = {
        "show_window": lambda: print("Show window: GUI not available in headless mode"),
        "run_preset": lambda preset: run_preset_direct(preset.get("name")),
        "open_settings": lambda: print("Settings: GUI not available in headless mode"),
        "exit_app": lambda: sys.exit(0),
    }

    tray = TrayManager(callbacks)
    tray.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tray.stop()


if __name__ == "__main__":
    sys.exit(main())
