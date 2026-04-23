"""Entry point for the ScreenHop application."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any, Callable

from src.browser_move import APP_NAME
from src.browser_move.config import load_config
from src.browser_move.dpi import setup_dpi_awareness
from src.browser_move.preset_runner import execute_preset
from src.browser_move.single_instance import (
    check_single_instance,
    show_already_running_message,
)
from src.browser_move.ui_theme import apply_base_theme


def main() -> int:
    """Main entry point for ScreenHop."""
    setup_dpi_awareness()

    if not check_single_instance():
        show_already_running_message()
        return 1

    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - launch and move Windows apps to a selected display"
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

    if args.headless:
        run_headless()
        return 0

    run_gui()
    return 0


def find_preset_by_name(config: dict, name: str) -> dict | None:
    for preset in config.get("presets", []):
        if preset.get("name") == name:
            return preset
    return None


def _cli_reporter(_status_type: str, message: str) -> None:
    print(message)


def run_preset_direct(preset_name: str) -> bool:
    """Execute preset directly without GUI."""
    config = load_config()
    preset = find_preset_by_name(config, preset_name)

    if not preset:
        print(f"Preset '{preset_name}' not found")
        return False

    return execute_preset(preset, reporter=_cli_reporter)


def run_gui() -> None:
    """Run in normal GUI mode with tray and window."""
    import customtkinter as ctk

    from src.browser_move.app import MainWindow
    from src.browser_move.tray import TrayManager

    config = load_config()
    apply_base_theme(config.get("theme", "System"))

    root = ctk.CTk()
    app = MainWindow(root)

    callbacks: dict[str, Callable] = {
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


def on_exit(root: Any, tray: Any | None) -> None:
    """Handle application exit."""
    if tray:
        tray.stop()
    root.quit()



def run_headless() -> None:
    """Run in headless mode (tray only, no GUI)."""
    from src.browser_move.tray import TrayManager

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
