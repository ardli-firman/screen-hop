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
from src.browser_move.ui_theme import (
    ACCENT,
    ACCENT_HOVER,
    BORDER,
    DANGER,
    MODAL_GEOMETRY,
    MODAL_MIN_SIZE,
    SUCCESS,
    SURFACE,
    SURFACE_ALT,
    TEXT_MUTED,
    WARN,
    apply_base_theme,
    font,
    style_card,
    style_panel,
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
        self.parent = parent
        self.on_apply = on_apply
        self.config = load_config()
        self.preset_names = self._resolve_preset_names(preset_names)
        self._selected_shortcut_preset = self._resolve_initial_shortcut_preset(selected_preset)
        self._startup_state = self._in_startup(self._selected_shortcut_preset or None)
        self.setup_ui()

    def setup_ui(self) -> None:
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(f"{APP_NAME} Settings")
        self.window.geometry(MODAL_GEOMETRY)
        self.window.minsize(*MODAL_MIN_SIZE)
        self.window.resizable(True, True)
        self.window.configure(fg_color=SURFACE)
        self.window.grab_set()
        self.window.transient(self.parent)
        self._center_window()

        shell = ctk.CTkFrame(self.window, fg_color="transparent")
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        main_card = ctk.CTkFrame(shell)
        style_panel(main_card)
        main_card.pack(fill="both", expand=True)

        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(20, 14))

        ctk.CTkLabel(
            header,
            text=f"{APP_NAME} Settings",
            font=font(20, "bold"),
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Tune the control panel, close behavior, and preset-based shortcuts in one place.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).pack(fill="x", pady=(4, 0))

        content = ctk.CTkScrollableFrame(main_card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        appearance_body = self._create_section(
            content,
            title="Workspace Feel",
            description="Adjust theme and what happens when you close the main window.",
        )

        ctk.CTkLabel(appearance_body, text="Theme", font=font(12, "bold"), anchor="w").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 12)
        )
        self.theme_combo = ctk.CTkComboBox(
            appearance_body,
            values=["Dark", "Light", "System"],
            state="readonly",
            height=38,
            corner_radius=14,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.theme_combo.set(self.config.get("theme", "System"))
        self.theme_combo.grid(row=0, column=1, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(
            appearance_body,
            text="Close Button",
            font=font(12, "bold"),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(0, 12))
        self.close_combo = ctk.CTkComboBox(
            appearance_body,
            values=["Exit", "Minimize to Tray"],
            state="readonly",
            height=38,
            corner_radius=14,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.close_combo.set(self.config.get("close_behavior", "Minimize to Tray"))
        self.close_combo.grid(row=1, column=1, sticky="ew")

        startup_body = self._create_section(
            content,
            title="Startup Behavior",
            description="Let Windows start one preset automatically using a shortcut in the Startup folder.",
        )

        self.auto_start_var = ctk.BooleanVar(value=self._startup_state)
        self.auto_start_check = ctk.CTkCheckBox(
            startup_body,
            text="Auto-run selected preset on Windows startup",
            variable=self.auto_start_var,
            font=font(12, "bold"),
            checkbox_width=20,
            checkbox_height=20,
        )
        self.auto_start_check.grid(row=0, column=0, columnspan=2, sticky="w")

        ctk.CTkLabel(
            startup_body,
            text="Startup uses the preset selected in Shortcut Target below.",
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        shortcuts_body = self._create_section(
            content,
            title="Shortcut Target",
            description="Desktop and Startup shortcuts both launch a preset by name so they stay in sync with the tray menu.",
        )

        ctk.CTkLabel(
            shortcuts_body,
            text="Preset",
            font=font(12, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 12))

        shortcut_values = self.preset_names if self.preset_names else ["No preset available"]
        shortcut_state = "readonly" if self.preset_names else "disabled"
        self.shortcut_preset_combo = ctk.CTkComboBox(
            shortcuts_body,
            values=shortcut_values,
            state=shortcut_state,
            command=self._on_shortcut_preset_changed,
            height=38,
            corner_radius=14,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.shortcut_preset_combo.grid(row=0, column=1, sticky="ew", pady=(0, 12))
        if self._selected_shortcut_preset:
            self.shortcut_preset_combo.set(self._selected_shortcut_preset)
        else:
            self.shortcut_preset_combo.set("No preset available")

        ctk.CTkLabel(
            shortcuts_body,
            text="Startup Status",
            font=font(12, "bold"),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(0, 12))

        self.startup_status_value = ctk.CTkLabel(
            shortcuts_body,
            text="Checking...",
            font=font(12, "bold"),
            anchor="e",
        )
        self.startup_status_value.grid(row=1, column=1, sticky="e", pady=(0, 12))

        desktop_btn = ctk.CTkButton(
            shortcuts_body,
            text="Create Desktop Shortcut",
            command=self.create_desktop_shortcut,
            height=40,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        desktop_btn.grid(row=2, column=0, sticky="ew", padx=(0, 8))

        self.startup_btn = ctk.CTkButton(
            shortcuts_body,
            text="Add to Startup",
            command=self.toggle_startup,
            height=40,
            corner_radius=14,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(12, "bold"),
        )
        self.startup_btn.grid(row=2, column=1, sticky="ew", padx=(8, 0))

        footer = ctk.CTkFrame(main_card, fg_color="transparent")
        footer.pack(fill="x", padx=22, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            footer,
            text="Cancel",
            command=self.window.destroy,
            height=42,
            width=130,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            font=font(13, "bold"),
        )
        cancel_btn.pack(side="right", padx=(0, 10))

        apply_btn = ctk.CTkButton(
            footer,
            text="Apply",
            command=self.apply_settings,
            height=42,
            width=150,
            corner_radius=14,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(13, "bold"),
        )
        apply_btn.pack(side="right")

        self._refresh_startup_ui(sync_checkbox=True)

    def _resolve_preset_names(self, preset_names: list[str] | None) -> list[str]:
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
        selected = str(selected_preset or "").strip()
        saved = str(self.config.get("shortcut_preset", "") or "").strip()

        if selected and selected in self.preset_names:
            return selected
        if saved and saved in self.preset_names:
            return saved
        if self.preset_names:
            return self.preset_names[0]
        return ""

    def _get_selected_preset(self) -> str:
        if not hasattr(self, "shortcut_preset_combo"):
            return self._selected_shortcut_preset

        selected = self.shortcut_preset_combo.get().strip()
        if selected in self.preset_names:
            return selected
        return ""

    def _on_shortcut_preset_changed(self, _choice: str) -> None:
        self._selected_shortcut_preset = self._get_selected_preset()
        self._refresh_startup_ui(sync_checkbox=True)

    def _create_section(
        self,
        parent: ctk.CTkScrollableFrame,
        title: str,
        description: str,
    ) -> ctk.CTkFrame:
        section = ctk.CTkFrame(parent)
        style_card(section)
        section.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(section, text=title, font=font(15, "bold"), anchor="w").pack(
            fill="x", padx=16, pady=(14, 2)
        )
        ctk.CTkLabel(
            section,
            text=description,
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).pack(fill="x", padx=16, pady=(0, 12))

        body = ctk.CTkFrame(section, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(0, 14))
        body.grid_columnconfigure(1, weight=1)
        return body

    def _center_window(self) -> None:
        window_width = 760
        window_height = 680

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

        self.window.geometry(f"{window_width}x{window_height}+{max(0, x)}+{max(0, y)}")

    def _in_startup(self, preset_name: str | None = None) -> bool:
        try:
            return is_in_startup(preset_name)
        except Exception as exc:
            print(f"[settings] Error checking startup status: {exc}")
            return False

    def _refresh_startup_ui(self, sync_checkbox: bool = False) -> None:
        preset_name = self._get_selected_preset()
        if not preset_name:
            self._startup_state = False
            self.startup_status_value.configure(text="No preset selected", text_color=TEXT_MUTED)
            self.startup_btn.configure(
                state="disabled",
                text="Add to Startup",
                fg_color=("#cfd9e6", "#233045"),
                hover_color=("#cfd9e6", "#233045"),
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
            self.startup_status_value.configure(text="Enabled", text_color=SUCCESS)
            self.startup_btn.configure(text="Remove from Startup", fg_color=WARN, hover_color=("#b5680c", "#d97706"))
        elif has_other_startup:
            self.startup_status_value.configure(text="Enabled for other preset", text_color=WARN)
            self.startup_btn.configure(text="Replace Startup Preset", fg_color=ACCENT, hover_color=ACCENT_HOVER)
        else:
            self.startup_status_value.configure(text="Disabled", text_color=TEXT_MUTED)
            self.startup_btn.configure(text="Add to Startup", fg_color=ACCENT, hover_color=ACCENT_HOVER)

        if sync_checkbox:
            self.auto_start_var.set(self._startup_state)

    def _set_startup_state(self, enabled: bool) -> bool:
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
        preset_name = self._get_selected_preset()
        if not preset_name:
            messagebox.showerror("Desktop Shortcut", "Select a preset target first.", parent=self.window)
            return

        try:
            success = ensure_single_desktop_shortcut(preset_name)
        except Exception as exc:
            print(f"[settings] Error creating desktop shortcut: {exc}")
            success = False

        if success:
            messagebox.showinfo(
                "Desktop Shortcut",
                f"Shortcut for preset '{preset_name}' was created on the Desktop.",
                parent=self.window,
            )
            return

        messagebox.showerror(
            "Desktop Shortcut",
            f"Failed to create Desktop shortcut for preset '{preset_name}'.",
            parent=self.window,
        )

    def toggle_startup(self) -> None:
        preset_name = self._get_selected_preset()
        if not preset_name:
            messagebox.showerror("Startup", "Select a preset target first.", parent=self.window)
            return

        selected_already_enabled = self._in_startup(preset_name)
        replace_mode = (not selected_already_enabled) and bool(get_all_startup_shortcuts())
        target_enabled = not selected_already_enabled
        success = self._set_startup_state(target_enabled)

        if not success:
            action_text = "enable" if target_enabled else "disable"
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
        selected_preset = self._get_selected_preset()
        desired_auto_start = self.auto_start_var.get()
        if desired_auto_start and not selected_preset:
            messagebox.showerror("Startup", "Select a preset target before enabling startup.", parent=self.window)
            return

        if not selected_preset:
            remove_all_startup_shortcuts()
            self._startup_state = False

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
        if not save_config(latest_config):
            messagebox.showerror("Settings", "Failed to save configuration.", parent=self.window)
            return

        self.config = latest_config
        apply_base_theme(settings["theme"])

        if self.on_apply:
            self.on_apply(settings)

        self.window.destroy()
