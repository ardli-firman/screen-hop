"""Entry point for the ScreenHop application."""

from __future__ import annotations

import argparse
import sys
import time

import customtkinter as ctk

from src.browser_move import APP_NAME
from src.browser_move.dpi import setup_dpi_awareness
from src.browser_move.single_instance import (
    check_single_instance,
    show_already_running_message,
)
from src.browser_move.app import MainWindow
from src.browser_move.tray import TrayManager
from src.browser_move.config import load_config
from src.browser_move.browsers import launch_browser
from src.browser_move.window_mover import (
    find_browser_window,
    move_window_to_monitor,
    list_browser_windows,
)
from src.browser_move.monitors import resolve_display_for_preset


def main() -> int:
    """Main entry point for ScreenHop.

    Returns:
        Exit code: 0 for success, 1 for error/already running
    """
    setup_dpi_awareness()

    if not check_single_instance():
        show_already_running_message()
        return 1

    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Launch and move browsers to a selected monitor"
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

    target_display, target_label, used_fallback = resolve_display_for_preset(preset)
    if not target_display:
        print("No multiple display detected (set Display mode to Extend)")
        return False

    if used_fallback:
        print(f"Saved display not found. Using {target_label}.")

    existing_hwnds = set(list_browser_windows(preset["browser_type"]))

    proc = launch_browser(
        preset["browser_type"],
        preset["url"],
        preset.get("kiosk_mode", False),
        preset.get("browser_path"),
    )

    if not proc:
        print("Failed to launch browser")
        return False

    hwnd = find_browser_window(
        preset["browser_type"], timeout=6.0, exclude_hwnds=existing_hwnds
    )
    if not hwnd:
        hwnd = find_browser_window(preset["browser_type"], timeout=4.0)
    if hwnd:
        moved = move_window_to_monitor(hwnd, target_display)
        if moved:
            print(f"Browser moved to {target_label}")
            return True
        for alt_hwnd in list_browser_windows(preset["browser_type"]):
            if alt_hwnd == hwnd:
                continue
            if move_window_to_monitor(alt_hwnd, target_display):
                print(f"Browser moved to {target_label}")
                return True

        print(f"Failed to move browser to {target_label}")
        return False

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
