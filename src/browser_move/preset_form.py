"""Preset management form UI for ScreenHop."""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

import customtkinter as ctk

from src.browser_move.config import load_config, save_config
from src.browser_move.launcher import is_valid_executable_path
from src.browser_move.monitors import get_display_choices
from src.browser_move.preset_templates import build_preset_template, get_template_choices
from src.browser_move.ui_theme import (
    ACCENT,
    ACCENT_HOVER,
    BORDER,
    DANGER,
    INFO,
    MODAL_GEOMETRY,
    MODAL_MIN_SIZE,
    SUCCESS,
    SURFACE,
    SURFACE_ALT,
    TEXT_MUTED,
    font,
    style_card,
    style_panel,
)


class PresetForm:
    """Modal form for adding/editing universal app presets."""

    def __init__(
        self,
        parent: ctk.CTk,
        preset: dict | None = None,
        on_save: Callable | None = None,
    ):
        self.parent = parent
        self.preset = preset
        self.on_save = on_save
        self.result = None
        self._display_id_by_label: dict[str, str] = {}
        self._display_label_by_id: dict[str, str] = {}
        self._template_id_by_label: dict[str, str] = {}
        self._advanced_visible = False
        self._feedback_color = TEXT_MUTED

        self.setup_ui()

    def setup_ui(self) -> None:
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Edit Preset" if self.preset else "New Preset")
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
        header.pack(fill="x", padx=22, pady=(20, 12))

        ctk.CTkLabel(
            header,
            text="Edit App Preset" if self.preset else "Create App Preset",
            font=font(20, "bold"),
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Pick a Windows executable, choose the target display, and add optional launch tuning only when needed.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).pack(fill="x", pady=(4, 0))

        form_body = ctk.CTkScrollableFrame(main_card, fg_color="transparent")
        form_body.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        form_body.grid_columnconfigure(0, weight=1)

        self._create_template_picker(form_body, row=0)

        self.name_entry = self._create_text_field(
            form_body,
            row=1,
            label="Preset Name",
            placeholder="OBS Studio - Display 2",
            helper="Use a short name that still makes sense in tray and startup shortcuts.",
        )

        self.path_entry = self._create_browse_field(
            form_body,
            row=2,
            label="Executable Path",
            button_text="Browse",
            placeholder="C:\\Program Files\\App\\app.exe",
            helper="Choose any .exe on Windows. ScreenHop will launch it exactly as configured.",
            command=self.browse_executable,
        )

        display_row = ctk.CTkFrame(form_body, fg_color="transparent")
        display_row.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        display_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            display_row,
            text="Target Display",
            font=font(12, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        monitor_input_row = ctk.CTkFrame(display_row, fg_color="transparent")
        monitor_input_row.grid(row=1, column=0, sticky="ew")
        monitor_input_row.grid_columnconfigure(0, weight=1)

        self.monitor_combo = ctk.CTkComboBox(
            monitor_input_row,
            values=["Loading displays..."],
            state="readonly",
            height=40,
            corner_radius=14,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.monitor_combo.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.refresh_monitors_btn = ctk.CTkButton(
            monitor_input_row,
            text="Refresh",
            width=96,
            height=40,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            command=self.refresh_monitor_choices,
            font=font(12, "bold"),
        )
        self.refresh_monitors_btn.grid(row=0, column=1)

        ctk.CTkLabel(
            display_row,
            text="Pick the display where the new app window should land after launch. If only one monitor is available, ScreenHop uses the main display.",
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        self.refresh_monitor_choices()

        advanced_toggle_row = ctk.CTkFrame(form_body, fg_color="transparent")
        advanced_toggle_row.grid(row=4, column=0, sticky="ew", pady=(4, 12))
        advanced_toggle_row.grid_columnconfigure(0, weight=1)

        self.advanced_toggle_btn = ctk.CTkButton(
            advanced_toggle_row,
            text="Show Advanced Options",
            command=self.toggle_advanced,
            height=38,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.advanced_toggle_btn.grid(row=0, column=0, sticky="w")

        self.advanced_frame = ctk.CTkFrame(form_body)
        style_card(self.advanced_frame, fg_color=("#eff7ff", "#132033"), border_color=INFO)
        self.advanced_frame.grid(row=5, column=0, sticky="ew", pady=(0, 14))
        self.advanced_frame.grid_columnconfigure(0, weight=1)

        self.launch_args_entry = self._create_text_field(
            self.advanced_frame,
            row=0,
            label="Launch Arguments",
            placeholder="--profile production --startvirtualcam",
            helper="Optional. Keep Windows-style quoting exactly as the app expects.",
            padx=14,
            pady_top=14,
        )

        self.working_dir_entry = self._create_browse_field(
            self.advanced_frame,
            row=1,
            label="Working Directory",
            button_text="Folder",
            placeholder="Leave empty to use the executable folder",
            helper="Optional. Use this when the app depends on a specific startup folder.",
            command=self.browse_working_directory,
            padx=14,
        )

        self.window_hint_entry = self._create_text_field(
            self.advanced_frame,
            row=2,
            label="Window Title Hint",
            placeholder="OBS / VLC / Dashboard",
            helper="Optional. Helps ScreenHop choose the right new window when the app opens more than one.",
            padx=14,
            pady_bottom=14,
        )

        self.feedback_label = ctk.CTkLabel(
            main_card,
            text="",
            font=font(11, "bold"),
            text_color=self._feedback_color,
            justify="left",
            wraplength=650,
            anchor="w",
        )
        self.feedback_label.pack(fill="x", padx=22, pady=(0, 12))

        footer = ctk.CTkFrame(main_card, fg_color="transparent")
        footer.pack(fill="x", padx=22, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)

        self.save_btn = ctk.CTkButton(
            footer,
            text="Update Preset" if self.preset else "Save Preset",
            command=self.save_preset,
            height=42,
            corner_radius=14,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(13, "bold"),
        )
        self.save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        if self.preset:
            self.delete_btn = ctk.CTkButton(
                footer,
                text="Delete",
                command=self.delete_preset,
                height=42,
                corner_radius=14,
                fg_color=DANGER,
                hover_color=("#b53d4d", "#dc2626"),
                font=font(13, "bold"),
            )
            self.delete_btn.grid(row=0, column=1, sticky="ew", padx=8)
        else:
            spacer = ctk.CTkFrame(footer, fg_color="transparent")
            spacer.grid(row=0, column=1, sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            footer,
            text="Cancel",
            command=self.window.destroy,
            height=42,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            font=font(13, "bold"),
        )
        self.cancel_btn.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        self._bind_clear_feedback(self.name_entry)
        self._bind_clear_feedback(self.path_entry)
        self._bind_clear_feedback(self.launch_args_entry)
        self._bind_clear_feedback(self.working_dir_entry)
        self._bind_clear_feedback(self.window_hint_entry)

        if self.preset:
            self._populate_fields()
            self._advanced_visible = any(
                str(self.preset.get(key, "")).strip()
                for key in ("launch_args", "working_directory", "window_title_hint")
            )
        else:
            self.template_combo.set("Blank / Manual")
        self._sync_advanced_state()

    def _create_template_picker(
        self,
        parent: ctk.CTkScrollableFrame,
        row: int,
    ) -> None:
        template_row = ctk.CTkFrame(parent)
        style_card(template_row, fg_color=("#f4f9ff", "#122033"), border_color=INFO)
        template_row.grid(row=row, column=0, sticky="ew", pady=(0, 14))
        template_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            template_row,
            text="Preset Template",
            font=font(12, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        selector_row = ctk.CTkFrame(template_row, fg_color="transparent")
        selector_row.grid(row=1, column=0, sticky="ew", padx=14)
        selector_row.grid_columnconfigure(0, weight=1)

        labels: list[str] = []
        for template_id, label in get_template_choices():
            labels.append(label)
            self._template_id_by_label[label] = template_id

        self.template_combo = ctk.CTkComboBox(
            selector_row,
            values=labels,
            state="readonly",
            height=40,
            corner_radius=14,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.template_combo.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        if labels:
            self.template_combo.set(labels[0])

        self.apply_template_btn = ctk.CTkButton(
            selector_row,
            text="Apply",
            command=self.apply_selected_template,
            width=96,
            height=40,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.apply_template_btn.grid(row=0, column=1)

        ctk.CTkLabel(
            template_row,
            text=(
                "Use built-in presets for common launch patterns. "
                "Browser Kiosk (Firefox) follows the launch parameters from docs/run.bat."
            ),
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).grid(row=2, column=0, sticky="w", padx=14, pady=(6, 14))

    def _create_text_field(
        self,
        parent: ctk.CTkFrame | ctk.CTkScrollableFrame,
        row: int,
        label: str,
        placeholder: str,
        helper: str,
        padx: int = 0,
        pady_top: int = 0,
        pady_bottom: int = 14,
    ) -> ctk.CTkEntry:
        field = ctk.CTkFrame(parent, fg_color="transparent")
        field.grid(row=row, column=0, sticky="ew", padx=padx, pady=(pady_top, pady_bottom))
        field.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(field, text=label, font=font(12, "bold"), anchor="w").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        entry = ctk.CTkEntry(
            field,
            height=40,
            corner_radius=14,
            placeholder_text=placeholder,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        entry.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(
            field,
            text=helper,
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))
        return entry

    def _create_browse_field(
        self,
        parent: ctk.CTkFrame | ctk.CTkScrollableFrame,
        row: int,
        label: str,
        button_text: str,
        placeholder: str,
        helper: str,
        command: Callable[[], None],
        padx: int = 0,
    ) -> ctk.CTkEntry:
        field = ctk.CTkFrame(parent, fg_color="transparent")
        field.grid(row=row, column=0, sticky="ew", padx=padx, pady=(0, 14))
        field.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(field, text=label, font=font(12, "bold"), anchor="w").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        input_row = ctk.CTkFrame(field, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew")
        input_row.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            input_row,
            height=40,
            corner_radius=14,
            placeholder_text=placeholder,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            input_row,
            text=button_text,
            command=command,
            width=96,
            height=40,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            font=font(12, "bold"),
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            field,
            text=helper,
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))
        return entry

    def _bind_clear_feedback(self, entry: ctk.CTkEntry) -> None:
        entry.bind("<KeyRelease>", lambda _event: self.set_feedback("", TEXT_MUTED))

    def toggle_advanced(self) -> None:
        self._advanced_visible = not self._advanced_visible
        self._sync_advanced_state()

    def _sync_advanced_state(self) -> None:
        if self._advanced_visible:
            self.advanced_frame.grid()
            self.advanced_toggle_btn.configure(text="Hide Advanced Options")
        else:
            self.advanced_frame.grid_remove()
            self.advanced_toggle_btn.configure(text="Show Advanced Options")

    def _center_window(self) -> None:
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        window_width = 760
        window_height = 680

        if parent_width <= 1 or parent_height <= 1:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        else:
            x = parent_x + (parent_width - window_width) // 2
            y = parent_y + (parent_height - window_height) // 2

        self.window.geometry(f"{window_width}x{window_height}+{max(0, x)}+{max(0, y)}")

    def _populate_fields(self) -> None:
        self.name_entry.insert(0, str(self.preset.get("name", "")))
        self.path_entry.insert(0, str(self.preset.get("executable_path", "")))
        self.launch_args_entry.insert(0, str(self.preset.get("launch_args", "")))
        self.working_dir_entry.insert(0, str(self.preset.get("working_directory", "")))
        self.window_hint_entry.insert(0, str(self.preset.get("window_title_hint", "")))
        self.template_combo.set("Blank / Manual")

        saved_display_id = str(self.preset.get("display_id", "")).strip()
        saved_display_name = str(self.preset.get("display_name", "")).strip()
        if saved_display_id and saved_display_id in self._display_label_by_id:
            self.monitor_combo.set(self._display_label_by_id[saved_display_id])
        elif saved_display_name and saved_display_name in self._display_id_by_label:
            self.monitor_combo.set(saved_display_name)

    def refresh_monitor_choices(self) -> None:
        current_label = self.monitor_combo.get() if hasattr(self, "monitor_combo") else ""

        self._display_id_by_label.clear()
        self._display_label_by_id.clear()

        choices = get_display_choices()
        if not choices:
            self.monitor_combo.configure(values=["No display detected"], state="disabled")
            self.monitor_combo.set("No display detected")
            return

        labels: list[str] = []
        for display_id, label in choices:
            labels.append(label)
            self._display_id_by_label[label] = display_id
            self._display_label_by_id[display_id] = label

        self.monitor_combo.configure(values=labels, state="readonly")
        if current_label in self._display_id_by_label:
            self.monitor_combo.set(current_label)
        elif labels:
            self.monitor_combo.set(labels[0])

    def browse_executable(self) -> None:
        selected_path = filedialog.askopenfilename(
            parent=self.window,
            title="Choose executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
        )
        if not selected_path:
            return

        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, selected_path)

        if not self.working_dir_entry.get().strip():
            self.working_dir_entry.insert(0, str(Path(selected_path).parent))
        self.set_feedback("", TEXT_MUTED)

    def browse_working_directory(self) -> None:
        initial_dir = self.working_dir_entry.get().strip()
        if not initial_dir:
            executable_path = self.path_entry.get().strip()
            if executable_path:
                initial_dir = str(Path(executable_path).parent)

        selected_dir = filedialog.askdirectory(
            parent=self.window,
            title="Choose working directory",
            initialdir=initial_dir or None,
        )
        if not selected_dir:
            return

        self.working_dir_entry.delete(0, "end")
        self.working_dir_entry.insert(0, selected_dir)
        self.set_feedback("", TEXT_MUTED)

    def _set_entry_value(self, entry: ctk.CTkEntry, value: str) -> None:
        entry.delete(0, "end")
        if value:
            entry.insert(0, value)

    def apply_selected_template(self) -> None:
        selected_label = self.template_combo.get().strip()
        template_id = self._template_id_by_label.get(selected_label, "")
        if not template_id or template_id == "blank":
            self.set_feedback("Blank template selected. Fill the preset manually.", INFO)
            return

        template_data = build_preset_template(template_id)
        if not template_data:
            self.set_feedback("Selected template is not available.", DANGER)
            return

        self._set_entry_value(self.name_entry, str(template_data.get("name", "")))
        self._set_entry_value(
            self.path_entry, str(template_data.get("executable_path", ""))
        )
        self._set_entry_value(
            self.launch_args_entry, str(template_data.get("launch_args", ""))
        )
        self._set_entry_value(
            self.working_dir_entry, str(template_data.get("working_directory", ""))
        )
        self._set_entry_value(
            self.window_hint_entry, str(template_data.get("window_title_hint", ""))
        )

        self._advanced_visible = True
        self._sync_advanced_state()

        template_notice = str(template_data.get("_template_notice", "")).strip()
        if template_notice:
            self.set_feedback(template_notice, INFO)
        else:
            self.set_feedback("Template applied.", INFO)

    def set_feedback(self, message: str, color: tuple[str, str]) -> None:
        self._feedback_color = color
        self.feedback_label.configure(text=message, text_color=color)

    def validate_form(self) -> tuple[bool, str]:
        name = self.name_entry.get().strip()
        executable_path = self.path_entry.get().strip()
        working_directory = self.working_dir_entry.get().strip()
        selected_display = self.monitor_combo.get().strip()

        if not name:
            return False, "Preset name is required."

        config = load_config()
        for preset in config.get("presets", []):
            existing_name = str(preset.get("name", "")).strip().lower()
            if existing_name != name.lower():
                continue
            if self.preset and str(self.preset.get("name", "")).strip().lower() == existing_name:
                continue
            return False, f"Preset name '{name}' already exists."

        if not executable_path:
            return False, "Executable path is required."
        if not is_valid_executable_path(executable_path):
            return False, "Executable path must point to an existing .exe file."

        if working_directory and not os.path.isdir(working_directory):
            return False, "Working directory must be an existing folder or left empty."

        if selected_display not in self._display_id_by_label:
            return False, "Please choose a valid target display."

        return True, ""

    def save_preset(self) -> None:
        is_valid, error_message = self.validate_form()
        if not is_valid:
            self.set_feedback(error_message, DANGER)
            return

        preset_data = {
            "name": self.name_entry.get().strip(),
            "executable_path": self.path_entry.get().strip(),
            "launch_args": self.launch_args_entry.get().strip(),
            "working_directory": self.working_dir_entry.get().strip(),
            "window_title_hint": self.window_hint_entry.get().strip(),
            "display_id": self._display_id_by_label[self.monitor_combo.get().strip()],
            "display_name": self.monitor_combo.get().strip(),
        }

        config = load_config()
        presets = config.get("presets", [])

        if self.preset:
            for index, existing in enumerate(presets):
                if existing.get("name") == self.preset.get("name"):
                    presets[index] = preset_data
                    break
        else:
            presets.append(preset_data)

        config["presets"] = presets
        if not save_config(config):
            self.set_feedback("Failed to save configuration.", DANGER)
            return

        self.result = preset_data
        self.set_feedback("Preset saved successfully.", SUCCESS)
        callback = self.on_save
        self.window.destroy()
        if callback:
            self.parent.after(0, lambda: callback(preset_data))

    def delete_preset(self) -> None:
        if not self.preset:
            return

        confirm = messagebox.askyesno(
            title="Delete Preset",
            message=f"Delete preset '{self.preset['name']}'?",
            parent=self.window,
        )
        if not confirm:
            return

        config = load_config()
        config["presets"] = [
            preset
            for preset in config.get("presets", [])
            if preset.get("name") != self.preset.get("name")
        ]

        if not save_config(config):
            self.set_feedback("Failed to delete preset.", DANGER)
            return

        self.set_feedback("Preset deleted.", INFO)
        callback = self.on_save
        self.window.destroy()
        if callback:
            self.parent.after(0, lambda: callback(None))
