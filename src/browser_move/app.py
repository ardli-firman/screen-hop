"""Main window UI for browser move automation."""

import customtkinter as ctk
from typing import Any

from src.browser_move.config import load_config
from src.browser_move.settings_window import SettingsWindow
from src.browser_move.preset_form import PresetForm
from src.browser_move.browsers import launch_browser
from src.browser_move.window_mover import (
    find_browser_window,
    move_window_to_monitor,
    list_browser_windows,
)
from src.browser_move.monitors import resolve_display_for_preset


class MainWindow:
    """Main application window for browser move automation."""

    def __init__(self, root: ctk.CTk, tray: Any = None):
        """Initialize main window.

        Args:
            root: CTk root window
            tray: Optional tray icon reference for minimize/restore
        """
        self.root = root
        self.tray = tray
        self.config = load_config()
        self._current_preset_var = ctk.StringVar(value="Select Preset")
        self._status_text = ctk.StringVar(value="Ready")

        self.setup_ui()
        self.setup_protocols()

    def setup_ui(self) -> None:
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root.title("Browser Move Automation")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        preset_label = ctk.CTkLabel(
            left_frame,
            text="Available Presets",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        preset_label.pack(fill="x", padx=5, pady=(5, 10))

        preset_names = self._get_preset_names()

        self.preset_combo = ctk.CTkComboBox(
            left_frame,
            values=preset_names,
            variable=self._current_preset_var,
            state="readonly",
            width=300,
            height=35,
        )
        self.preset_combo.pack(fill="x", padx=5, pady=5)
        if preset_names:
            self.preset_combo.set(preset_names[0])

        self.preset_count_label = ctk.CTkLabel(
            left_frame,
            text=f"{len(preset_names)} preset(s) available",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.preset_count_label.pack(fill="x", padx=5, pady=10)

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)

        self.run_btn = ctk.CTkButton(
            right_frame,
            text="Run Preset",
            command=self.run_preset,
            height=45,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.run_btn.pack(pady=10, padx=10)

        self.new_btn = ctk.CTkButton(
            right_frame,
            text="New Preset",
            command=self.new_preset,
            height=40,
            width=150,
        )
        self.new_btn.pack(pady=5, padx=10)

        self.edit_btn = ctk.CTkButton(
            right_frame,
            text="Edit Preset",
            command=self.edit_preset,
            height=40,
            width=150,
        )
        self.edit_btn.pack(pady=5, padx=10)

        self.settings_btn = ctk.CTkButton(
            right_frame,
            text="Settings",
            command=self.open_settings,
            height=40,
            width=150,
        )
        self.settings_btn.pack(pady=5, padx=10)

        status_frame = ctk.CTkFrame(self.root, height=40)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self._status_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_label.pack(side="left", padx=10, fill="both", expand=True)

        version_label = ctk.CTkLabel(
            status_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="e",
        )
        version_label.pack(side="right", padx=10)

    def setup_protocols(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def _get_preset_names(self) -> list[str]:
        presets = self.config.get("presets", [])
        if not presets:
            return []

        names = []
        for preset in presets:
            if isinstance(preset, dict) and "name" in preset:
                names.append(preset["name"])

        return names

    def minimize_to_tray(self) -> None:
        self.root.withdraw()

    def show_window(self) -> None:
        self.root.deiconify()
        self.root.focus_force()

    def run_preset(self) -> None:
        selected_name = self.preset_combo.get()
        if not selected_name or selected_name == "Select Preset":
            self.update_status("Please select a preset first")
            return

        self.run_preset_by_name(selected_name)

    def run_preset_by_name(self, name: str) -> bool:
        preset = self._find_preset_by_name(name)
        if not preset:
            self.update_status(f"Preset '{name}' not found")
            return False

        return self._execute_preset(preset)

    def _find_preset_by_name(self, name: str) -> dict | None:
        for preset in self.config.get("presets", []):
            if preset.get("name") == name:
                return preset
        return None

    def _execute_preset(self, preset: dict) -> bool:
        target_display, target_label, used_fallback = resolve_display_for_preset(preset)
        if not target_display:
            self.update_status("No multiple display detected (set Display mode to Extend)")
            return False

        if used_fallback:
            self.update_status(
                f"Saved display not found, using {target_label}. Launching {preset['browser_type']}..."
            )
        else:
            self.update_status(
                f"Launching {preset['browser_type']} on {target_label}..."
            )

        existing_hwnds = set(list_browser_windows(preset["browser_type"]))

        proc = launch_browser(
            preset["browser_type"],
            preset["url"],
            preset.get("kiosk_mode", False),
            preset.get("browser_path"),
        )

        if not proc:
            self.update_status("Failed to launch browser")
            return False

        self.update_status("Finding launched browser window...")

        # Prefer newly appeared windows after launch; fallback to any browser window.
        hwnd = find_browser_window(
            preset["browser_type"], timeout=6.0, exclude_hwnds=existing_hwnds
        )
        if not hwnd:
            hwnd = find_browser_window(preset["browser_type"], timeout=4.0)
        if hwnd:
            moved = move_window_to_monitor(hwnd, target_display)
            if moved:
                self.update_status(f"Browser moved to {target_label}")
                return True
            # Fallback: browser may have spawned a different top-level window.
            for alt_hwnd in list_browser_windows(preset["browser_type"]):
                if alt_hwnd == hwnd:
                    continue
                if move_window_to_monitor(alt_hwnd, target_display):
                    self.update_status(f"Browser moved to {target_label}")
                    return True

            self.update_status(f"Failed to move browser to {target_label}")
            return False

        self.update_status("Failed to find browser window")
        return False

    def new_preset(self) -> None:
        self.update_status("Creating new preset...")
        self._open_preset_form(preset=None)

    def edit_preset(self) -> None:
        selected_name = self.preset_combo.get()
        if not selected_name or selected_name == "Select Preset":
            self.update_status("Please select a preset to edit")
            return

        preset = self._find_preset_by_name(selected_name)
        if not preset:
            self.update_status(f"Preset '{selected_name}' not found")
            return

        self.update_status(f"Editing preset '{selected_name}'...")
        self._open_preset_form(preset=preset)

    def _open_preset_form(self, preset: dict | None) -> None:
        is_edit = preset is not None
        action_state = {"action": "cancelled"}

        def on_preset_saved(saved_preset: dict | None) -> None:
            action_state["action"] = "saved" if saved_preset else "deleted"
            self._reload_presets()
            if self.tray:
                self.tray.update_menu()

            if saved_preset and "name" in saved_preset:
                self.preset_combo.set(saved_preset["name"])
                status_action = "updated" if is_edit else "created"
                self.update_status(f"Preset '{saved_preset['name']}' {status_action}")
            elif preset and "name" in preset:
                self.update_status(f"Preset '{preset['name']}' deleted")
            else:
                self.update_status("Preset list updated")

        form = PresetForm(self.root, preset=preset, on_save=on_preset_saved)
        form.window.wait_window()

        if action_state["action"] == "cancelled":
            if is_edit:
                self.update_status("Preset edit cancelled")
            else:
                self.update_status("Preset creation cancelled")

    def open_settings(self) -> None:
        self.update_status("Opening settings...")

        def on_settings_applied(settings: dict) -> None:
            self.config.update(settings)
            self.update_status("Settings applied")

        SettingsWindow(self.root, on_apply=on_settings_applied)

    def update_status(self, message: str) -> None:
        """Update status bar message.

        Args:
            message: Status message to display
        """
        self._status_text.set(message)
        self.status_label.configure(text=message)

    def _reload_presets(self) -> None:
        """Reload presets from config and refresh preset-related UI."""
        self.config = load_config()
        preset_names = self._get_preset_names()

        combo_values = preset_names if preset_names else ["Select Preset"]
        self.preset_combo.configure(values=combo_values)

        if preset_names:
            current = self._current_preset_var.get()
            if current in preset_names:
                self.preset_combo.set(current)
            else:
                self.preset_combo.set(preset_names[0])
        else:
            self.preset_combo.set("Select Preset")

        self.preset_count_label.configure(text=f"{len(preset_names)} preset(s) available")
