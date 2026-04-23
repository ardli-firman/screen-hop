"""Settings dialog for ScreenHop."""

from __future__ import annotations

from tkinter import messagebox
from typing import Callable

import customtkinter as ctk

from src.browser_move import APP_NAME
from src.browser_move.config import load_config, save_config
from src.browser_move.shortcuts import (
    ensure_single_desktop_shortcut,
    ensure_single_startup_shortcut,
    get_all_startup_shortcuts,
    is_in_startup,
    remove_all_startup_shortcuts,
)


class SettingsWindow:
    """Settings modal dialog for ScreenHop."""

    def __init__(
        self,
        parent: ctk.CTk,
        on_apply: Callable[[dict], None] | None = None,
        preset_names: list[str] | None = None,
        selected_preset: str | None = None,
    ):
        """Initialize settings window.

        Args:
            parent: Parent CTk window
            on_apply: Optional callback called with settings dict after Apply
        """
        self.parent = parent
        self.on_apply = on_apply
        self.config = load_config()
        self.preset_names = self._resolve_preset_names(preset_names)
        self._selected_shortcut_preset = self._resolve_initial_shortcut_preset(
            selected_preset
        )
        self._startup_state = self._in_startup(self._selected_shortcut_preset or None)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Build the settings UI."""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(f"{APP_NAME} Settings")
        self.window.geometry("560x620")
        self.window.minsize(520, 560)
        self.window.resizable(True, True)
        self.window.grab_set()
        self.window.transient(self.parent)
        self._center_window()

        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(4, 12))

        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{APP_NAME} Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Customize app behavior, startup, and shortcuts.",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            anchor="w",
        )
        subtitle_label.pack(fill="x", pady=(2, 0))

        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        appearance_body = self._create_section(
            content_frame,
            title="Appearance",
            description="Set application theme and close-window behavior.",
        )

        theme_label = ctk.CTkLabel(
            appearance_body,
            text="Theme",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        theme_label.grid(row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 12))

        self.theme_combo = ctk.CTkComboBox(
            appearance_body,
            values=["Dark", "Light", "System"],
            state="readonly",
            height=36,
            width=170,
        )
        self.theme_combo.set(self.config.get("theme", "System"))
        self.theme_combo.grid(row=0, column=1, sticky="ew", pady=(0, 12))

        close_label = ctk.CTkLabel(
            appearance_body,
            text="Close Button",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        close_label.grid(row=1, column=0, sticky="w", padx=(0, 12))

        self.close_combo = ctk.CTkComboBox(
            appearance_body,
            values=["Exit", "Minimize to Tray"],
            state="readonly",
            height=36,
            width=170,
        )
        self.close_combo.set(self.config.get("close_behavior", "Minimize to Tray"))
        self.close_combo.grid(row=1, column=1, sticky="ew")

        startup_body = self._create_section(
            content_frame,
            title="Startup",
            description="Auto-run the selected preset when Windows starts.",
        )

        self.auto_start_var = ctk.BooleanVar(value=self._startup_state)
        self.auto_start_check = ctk.CTkCheckBox(
            startup_body,
            text="Auto-run selected preset on startup",
            variable=self.auto_start_var,
            font=ctk.CTkFont(size=13),
            checkbox_width=20,
            checkbox_height=20,
        )
        self.auto_start_check.grid(row=0, column=0, columnspan=2, sticky="w")

        startup_hint = ctk.CTkLabel(
            startup_body,
            text="Uses Preset Target from the Shortcuts section.",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            anchor="w",
        )
        startup_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

        shortcuts_body = self._create_section(
            content_frame,
            title="Shortcuts",
            description="Shortcut target must be a preset so click/startup can run it directly.",
        )

        shortcut_target_label = ctk.CTkLabel(
            shortcuts_body,
            text="Preset Target",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        shortcut_target_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 12))

        shortcut_combo_values = self.preset_names if self.preset_names else ["No preset available"]
        shortcut_combo_state = "readonly" if self.preset_names else "disabled"
        self.shortcut_preset_combo = ctk.CTkComboBox(
            shortcuts_body,
            values=shortcut_combo_values,
            state=shortcut_combo_state,
            command=self._on_shortcut_preset_changed,
            height=36,
        )
        self.shortcut_preset_combo.grid(row=0, column=1, sticky="ew", pady=(0, 12))
        if self._selected_shortcut_preset:
            self.shortcut_preset_combo.set(self._selected_shortcut_preset)
        else:
            self.shortcut_preset_combo.set("No preset available")

        startup_status_label = ctk.CTkLabel(
            shortcuts_body,
            text="Startup Shortcut Status",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        startup_status_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 12))

        self.startup_status_value = ctk.CTkLabel(
            shortcuts_body,
            text="Checking...",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="e",
        )
        self.startup_status_value.grid(row=1, column=1, sticky="e", pady=(0, 12))

        desktop_btn = ctk.CTkButton(
            shortcuts_body,
            text="Create Desktop Shortcut",
            command=self.create_desktop_shortcut,
            height=38,
            width=220,
        )
        desktop_btn.grid(row=2, column=0, sticky="ew", padx=(0, 8))

        self.startup_btn = ctk.CTkButton(
            shortcuts_body,
            text="Add to Startup",
            command=self.toggle_startup,
            height=38,
            width=220,
        )
        self.startup_btn.grid(row=2, column=1, sticky="ew", padx=(8, 0))

        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(4, 0))

        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancel",
            command=self.window.destroy,
            height=40,
            width=120,
            fg_color="transparent",
            border_width=2,
        )
        cancel_btn.pack(side="right", padx=(0, 10))

        apply_btn = ctk.CTkButton(
            footer_frame,
            text="Apply",
            command=self.apply_settings,
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        apply_btn.pack(side="right")

        self._refresh_startup_ui(sync_checkbox=True)

    def _resolve_preset_names(self, preset_names: list[str] | None) -> list[str]:
        """Resolve preset names from argument or config."""
        names = preset_names
        if names is None:
            names = [
                preset.get("name", "")
                for preset in self.config.get("presets", [])
                if isinstance(preset, dict)
            ]

        cleaned: list[str] = []
        for name in names:
            value = str(name).strip()
            if value and value not in cleaned:
                cleaned.append(value)

        return cleaned

    def _resolve_initial_shortcut_preset(self, selected_preset: str | None) -> str:
        """Choose initial preset target for shortcut and startup actions."""
        selected = (selected_preset or "").strip()
        saved = str(self.config.get("shortcut_preset", "") or "").strip()

        if selected and selected in self.preset_names:
            return selected
        if saved and saved in self.preset_names:
            return saved
        if self.preset_names:
            return self.preset_names[0]
        return ""

    def _get_selected_preset(self) -> str:
        """Get currently selected preset from shortcut target dropdown."""
        if not hasattr(self, "shortcut_preset_combo"):
            return self._selected_shortcut_preset

        selected = self.shortcut_preset_combo.get().strip()
        if selected in self.preset_names:
            return selected
        return ""

    def _on_shortcut_preset_changed(self, _choice: str) -> None:
        """Refresh startup controls when target preset changes."""
        self._selected_shortcut_preset = self._get_selected_preset()
        self._refresh_startup_ui(sync_checkbox=True)

    def _create_section(
        self,
        parent: ctk.CTkScrollableFrame,
        title: str,
        description: str,
    ) -> ctk.CTkFrame:
        """Create a settings section with heading and content body."""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill="x", pady=(0, 12))

        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x", padx=16, pady=(14, 2))

        description_label = ctk.CTkLabel(
            section_frame,
            text=description,
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            anchor="w",
        )
        description_label.pack(fill="x", padx=16, pady=(0, 12))

        body = ctk.CTkFrame(section_frame, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(0, 14))
        body.grid_columnconfigure(1, weight=1)
        return body

    def _center_window(self) -> None:
        """Center settings window over parent."""
        window_width = 560
        window_height = 620

        self.parent.update_idletasks()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        if parent_width <= 1 or parent_height <= 1:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        else:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            x = parent_x + (parent_width - window_width) // 2
            y = parent_y + (parent_height - window_height) // 2

        x = max(0, x)
        y = max(0, y)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _in_startup(self, preset_name: str | None = None) -> bool:
        """Check if app is in Windows startup folder."""
        try:
            return is_in_startup(preset_name)
        except Exception as exc:
            print(f"[settings] Error checking startup status: {exc}")
            return False

    def _refresh_startup_ui(self, sync_checkbox: bool = False) -> None:
        """Refresh startup status text, startup button text, and optional checkbox."""
        preset_name = self._get_selected_preset()
        if not preset_name:
            self._startup_state = False
            self.startup_status_value.configure(text="No preset selected", text_color="gray60")
            self.startup_btn.configure(
                state="disabled",
                text="Add to Startup",
                fg_color="gray50",
                hover_color="gray45",
            )
            self.auto_start_check.configure(state="disabled")

            if sync_checkbox:
                self.auto_start_var.set(False)
            return

        self.auto_start_check.configure(state="normal")
        self.startup_btn.configure(state="normal")
        self._startup_state = self._in_startup(preset_name)
        has_other_startup = bool(get_all_startup_shortcuts()) and not self._startup_state

        if self._startup_state:
            self.startup_status_value.configure(text="Enabled", text_color="#2e8b57")
            self.startup_btn.configure(
                text="Remove from Startup",
                fg_color="#d97706",
                hover_color="#b45309",
            )
        elif has_other_startup:
            self.startup_status_value.configure(
                text="Enabled for other preset",
                text_color="#d97706",
            )
            self.startup_btn.configure(
                text="Replace Startup Preset",
                fg_color="#2563eb",
                hover_color="#1d4ed8",
            )
        else:
            self.startup_status_value.configure(text="Disabled", text_color="gray60")
            self.startup_btn.configure(
                text="Add to Startup",
                fg_color="#2563eb",
                hover_color="#1d4ed8",
            )

        if sync_checkbox:
            self.auto_start_var.set(self._startup_state)

    def _set_startup_state(self, enabled: bool) -> bool:
        """Enable or disable startup shortcut."""
        preset_name = self._get_selected_preset()
        if not preset_name:
            return False

        try:
            if enabled:
                success = ensure_single_startup_shortcut(preset_name)
            else:
                remove_all_startup_shortcuts()
                success = not bool(get_all_startup_shortcuts())
        except Exception as exc:
            print(f"[settings] Error changing startup shortcut: {exc}")
            return False

        if not success:
            return False

        self._refresh_startup_ui(sync_checkbox=True)
        return self._startup_state == enabled

    def create_desktop_shortcut(self) -> None:
        """Create desktop shortcut for the application."""
        preset_name = self._get_selected_preset()
        if not preset_name:
            messagebox.showerror(
                "Desktop Shortcut",
                "Please select a preset target first.",
                parent=self.window,
            )
            return

        try:
            success = ensure_single_desktop_shortcut(preset_name)
        except Exception as exc:
            print(f"[settings] Error creating desktop shortcut: {exc}")
            success = False

        if success:
            messagebox.showinfo(
                "Desktop Shortcut",
                f"Shortcut for preset '{preset_name}' created on Desktop. Existing ScreenHop shortcut was replaced automatically.",
                parent=self.window,
            )
            return

        messagebox.showerror(
            "Desktop Shortcut",
            f"Failed to create Desktop shortcut for preset '{preset_name}'.",
            parent=self.window,
        )

    def toggle_startup(self) -> None:
        """Toggle app in Windows startup folder immediately."""
        preset_name = self._get_selected_preset()
        if not preset_name:
            messagebox.showerror(
                "Startup",
                "Please select a preset target first.",
                parent=self.window,
            )
            return

        selected_already_enabled = self._in_startup(preset_name)
        replace_mode = (not selected_already_enabled) and bool(get_all_startup_shortcuts())
        target_enabled = not selected_already_enabled
        success = self._set_startup_state(target_enabled)

        if not success:
            action_text = "add to" if target_enabled else "remove from"
            messagebox.showerror(
                "Startup",
                f"Failed to {action_text} startup for preset '{preset_name}'.",
                parent=self.window,
            )
            return

        if target_enabled and replace_mode:
            action_text = "replaced and added to"
        else:
            action_text = "added to" if target_enabled else "removed from"
        messagebox.showinfo(
            "Startup",
            f"Preset '{preset_name}' has been {action_text} startup.",
            parent=self.window,
        )

    def apply_settings(self) -> None:
        """Save settings to config and trigger callback."""
        selected_preset = self._get_selected_preset()
        desired_auto_start = self.auto_start_var.get()
        if desired_auto_start and not selected_preset:
            messagebox.showerror(
                "Startup",
                "Select a preset target before enabling startup.",
                parent=self.window,
            )
            return

        if selected_preset and not self._set_startup_state(desired_auto_start):
            action_text = "enable" if desired_auto_start else "disable"
            messagebox.showerror(
                "Startup",
                f"Could not {action_text} startup for preset '{selected_preset}'.",
                parent=self.window,
            )
            return

        settings = {
            "theme": self.theme_combo.get(),
            "auto_start": self._startup_state if selected_preset else False,
            "close_behavior": self.close_combo.get(),
            "shortcut_preset": selected_preset,
            "startup_preset": selected_preset if self._startup_state else "",
        }

        latest_config = load_config()
        latest_config.update(settings)
        saved = save_config(latest_config)
        if not saved:
            messagebox.showerror(
                "Settings",
                "Failed to save configuration.",
                parent=self.window,
            )
            return

        self.config = latest_config
        ctk.set_appearance_mode(settings["theme"])

        print(f"[settings] Settings applied: {settings}")

        if self.on_apply:
            self.on_apply(settings)

        self.window.destroy()
