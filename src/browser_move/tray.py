"""System tray icon manager using pystray."""

from pathlib import Path
from typing import Callable, Dict, Any, Optional

import pystray
from PIL import Image

from src.browser_move import APP_NAME


class TrayManager:
    """Manages system tray icon with menu actions."""

    def __init__(self, callbacks: Dict[str, Callable]):
        """Initialize tray manager.

        Args:
            callbacks: Dictionary of callback functions:
                - show_window: Called when user wants to show main window
                - run_preset: Called with preset dict when user selects preset
                - open_settings: Called when user wants to open settings
                - exit_app: Called when user wants to exit application
        """
        self.callbacks = callbacks
        self.icon: Optional[Any] = None
        self._setup_icon()

    def _setup_icon(self) -> None:
        """Set up the tray icon with menu."""
        icon_path = Path(__file__).parent.parent.parent / "icon.ico"

        try:
            image = Image.open(icon_path)
        except FileNotFoundError:
            print(f"[tray] Icon not found at {icon_path}, creating placeholder")
            image = Image.new("RGBA", (64, 64), color=(0, 120, 212, 255))

        menu = self._create_menu()

        self.icon = pystray.Icon(
            APP_NAME,
            image,
            APP_NAME,
            menu=menu,
        )
        if self.icon:
            self.icon.on_double_click = self._on_double_click

    def _create_menu(self) -> pystray.Menu:
        """Create the tray menu with preset submenu.

        Returns:
            pystray.Menu object
        """
        from src.browser_move.config import load_config

        config = load_config()
        presets = config.get("presets", [])

        preset_items = []
        for preset in presets:
            if isinstance(preset, dict) and "name" in preset:
                preset_items.append(
                    pystray.MenuItem(
                        preset["name"],
                        self._make_run_preset_action(preset),
                    )
                )

        if not preset_items:
            preset_items = [
                pystray.MenuItem("No presets", lambda icon, item: None, enabled=False)
            ]

        return pystray.Menu(
            pystray.MenuItem("Show Window", self._on_show, default=True),
            pystray.MenuItem("Run Preset", pystray.Menu(*preset_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self._on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit),
        )

    def _make_run_preset_action(self, preset: Dict[str, Any]) -> Callable[[], None]:
        """Create a pystray-compatible callback for a specific preset.

        pystray validates callback signatures and rejects callables that
        require more than two positional arguments.
        """

        def action() -> None:
            self._on_run_preset(preset)

        return action

    def _on_double_click(self, icon: Any, item: Optional[Any]) -> None:
        """Handle double-click on tray icon.

        Args:
            icon: The tray icon instance
            item: The clicked item (usually None for icon double-click)
        """
        self._on_show(icon, item)

    def _on_show(self, icon: Any, item: Optional[Any]) -> None:
        """Handle Show Window menu click.

        Args:
            icon: The tray icon instance
            item: The clicked menu item
        """
        callback = self.callbacks.get("show_window")
        if callback:
            callback()

    def _on_run_preset(self, preset: Dict[str, Any]) -> None:
        """Handle Run Preset menu selection.

        Args:
            preset: The preset dictionary to run
        """
        callback = self.callbacks.get("run_preset")
        if callback:
            callback(preset)

    def _on_settings(self, icon: Any, item: Optional[Any]) -> None:
        """Handle Settings menu click.

        Args:
            icon: The tray icon instance
            item: The clicked menu item
        """
        callback = self.callbacks.get("open_settings")
        if callback:
            callback()

    def _on_exit(self, icon: Any, item: Optional[Any]) -> None:
        """Handle Exit menu click.

        Args:
            icon: The tray icon instance
            item: The clicked menu item
        """
        callback = self.callbacks.get("exit_app")
        if callback:
            callback()

    def start(self) -> None:
        """Start the tray icon (non-blocking).

        Uses run_detached() to run in a separate thread,
        which is safe for use with Tkinter's main loop.
        """
        if self.icon:
            self.icon.run_detached()
            print("[tray] Tray icon started")

    def stop(self) -> None:
        """Stop the tray icon."""
        if self.icon:
            self.icon.stop()
            print("[tray] Tray icon stopped")

    def update_menu(self) -> None:
        """Refresh the menu to reflect updated presets.

        This should be called after presets are added, removed, or modified.
        """
        if self.icon:
            self.icon.menu = self._create_menu()
            print("[tray] Menu updated")
