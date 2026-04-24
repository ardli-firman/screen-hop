"""Main window UI for ScreenHop."""

from __future__ import annotations

from pathlib import Path
from tkinter import TclError
from typing import Any

import customtkinter as ctk

from src.browser_move import APP_NAME, __version__
from src.browser_move.config import consume_runtime_notices, get_preset_programs, load_config
from src.browser_move.preset_form import PresetForm
from src.browser_move.preset_runner import execute_preset
from src.browser_move.settings_window import SettingsWindow
from src.browser_move.status_bar import StatusBar
from src.browser_move.ui_theme import (
    ACCENT,
    ACCENT_HOVER,
    APP_CONTENT_MAX_WIDTH,
    APP_GEOMETRY,
    APP_MIN_SIZE,
    BORDER,
    DISABLED,
    INFO,
    INNER_RADIUS,
    SURFACE,
    SURFACE_ALT,
    SURFACE_MUTED,
    TEXT_MUTED,
    WARN,
    apply_base_theme,
    font,
    style_card,
    style_panel,
)


class MainWindow:
    """Main application window for ScreenHop."""

    def __init__(self, root: ctk.CTk, tray: Any = None):
        self.root = root
        self.tray = tray
        self.config = load_config()
        self._runtime_notices = consume_runtime_notices()
        self._search_var = ctk.StringVar(value="")
        self._selected_preset_name = ""

        self.setup_ui()
        self.setup_protocols()
        self._reload_presets(initial=True)

    def setup_ui(self) -> None:
        apply_base_theme(self.config.get("theme", "System"))

        self.root.title(APP_NAME)
        self.root.geometry(APP_GEOMETRY)
        self.root.minsize(*APP_MIN_SIZE)
        self.root.configure(fg_color=SURFACE)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        outer = ctk.CTkFrame(self.root, fg_color="transparent")
        outer.grid(row=0, column=0, sticky="nsew", padx=16, pady=14)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        self.shell = ctk.CTkFrame(outer, fg_color="transparent", width=APP_CONTENT_MAX_WIDTH)
        self.shell.grid(row=0, column=0, sticky="ns")
        self.shell.grid_propagate(False)
        self.shell.grid_columnconfigure(0, weight=1)
        self.shell.grid_rowconfigure(1, weight=1)
        self.root.bind("<Configure>", self._sync_shell_width, add="+")
        self.root.after(0, self._sync_shell_width)

        topbar = ctk.CTkFrame(self.shell, height=46)
        style_panel(topbar)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)
        topbar.grid_rowconfigure(0, weight=1)

        brand_row = ctk.CTkFrame(topbar, fg_color="transparent")
        brand_row.grid(row=0, column=0, sticky="w", padx=14, pady=8)

        ctk.CTkLabel(
            brand_row,
            text=APP_NAME,
            font=font(16, "bold"),
            anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            brand_row,
            text=f"v{__version__}",
            font=font(10, "bold"),
            text_color=TEXT_MUTED,
            fg_color=SURFACE_MUTED,
            corner_radius=999,
            padx=8,
            pady=2,
        ).pack(side="left", padx=(8, 0))

        self.settings_btn = ctk.CTkButton(
            topbar,
            text="Settings",
            command=self.open_settings,
            width=96,
            height=32,
            corner_radius=INNER_RADIUS,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE_MUTED,
            border_width=1,
            border_color=BORDER,
            font=font(11, "bold"),
        )
        self.settings_btn.grid(row=0, column=1, sticky="e", padx=12, pady=7)

        body = ctk.CTkFrame(self.shell, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(body, width=320)
        style_panel(self.sidebar)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(3, weight=1)

        sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        sidebar_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar_header,
            text="Presets",
            font=font(13, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.preset_count_label = ctk.CTkLabel(
            sidebar_header,
            text="0 presets",
            font=font(11, "bold"),
            text_color=TEXT_MUTED,
            anchor="e",
        )
        self.preset_count_label.grid(row=0, column=1, sticky="e")

        self.new_btn = ctk.CTkButton(
            self.sidebar,
            text="New Preset",
            command=self.new_preset,
            height=34,
            corner_radius=INNER_RADIUS,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(12, "bold"),
        )
        self.new_btn.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.notice_frame = ctk.CTkFrame(self.sidebar)
        style_card(self.notice_frame, fg_color=("#fff4e5", "#3a2a0e"), border_color=WARN)
        self.notice_label = ctk.CTkLabel(
            self.notice_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=232,
            font=font(10, "bold"),
        )
        self.notice_label.pack(fill="x", padx=10, pady=8)

        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            textvariable=self._search_var,
            height=34,
            corner_radius=INNER_RADIUS,
            placeholder_text="Search presets...",
            border_color=BORDER,
            font=font(11, "bold"),
        )
        self.search_entry.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        self._search_var.trace_add("write", lambda *_args: self._render_preset_list())

        self.preset_list_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0,
        )
        self.preset_list_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.preset_list_frame.grid_columnconfigure(0, weight=1)

        self.details_card = ctk.CTkFrame(body)
        style_panel(self.details_card)
        self.details_card.grid(row=0, column=1, sticky="nsew")
        self.details_card.grid_columnconfigure(0, weight=1)
        self.details_card.grid_rowconfigure(1, weight=1)

        details_header = ctk.CTkFrame(self.details_card, fg_color="transparent")
        details_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 10))
        details_header.grid_columnconfigure(0, weight=1)

        self.detail_title = ctk.CTkLabel(
            details_header,
            text="No preset selected",
            font=font(18, "bold"),
            anchor="w",
            justify="left",
            wraplength=620,
        )
        self.detail_title.grid(row=0, column=0, sticky="ew")

        self.detail_subtitle = ctk.CTkLabel(
            details_header,
            text="Choose a preset on the left or create a new one.",
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=620,
        )
        self.detail_subtitle.grid(row=1, column=0, sticky="ew", pady=(2, 8))

        action_stack = ctk.CTkFrame(details_header, fg_color="transparent")
        action_stack.grid(row=2, column=0, sticky="ew")
        action_stack.grid_columnconfigure(1, weight=1)

        self.detail_badge = ctk.CTkLabel(
            action_stack,
            text="No preset",
            font=font(10, "bold"),
            fg_color=("#e7efff", "#17294a"),
            text_color=INFO,
            corner_radius=999,
            padx=10,
            pady=3,
        )
        self.detail_badge.grid(row=0, column=0, sticky="w")

        action_buttons = ctk.CTkFrame(action_stack, fg_color="transparent")
        action_buttons.grid(row=0, column=2, sticky="e")

        self.run_btn = ctk.CTkButton(
            action_buttons,
            text="Launch & Move",
            command=self.run_preset,
            width=128,
            height=34,
            corner_radius=INNER_RADIUS,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(12, "bold"),
        )
        self.run_btn.pack(side="left")

        self.edit_btn = ctk.CTkButton(
            action_buttons,
            text="Edit",
            command=self.edit_preset,
            width=76,
            height=34,
            corner_radius=INNER_RADIUS,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE_MUTED,
            border_width=1,
            border_color=BORDER,
            font=font(12, "bold"),
        )
        self.edit_btn.pack(side="left", padx=(8, 0))

        self.program_details_frame = ctk.CTkScrollableFrame(
            self.details_card,
            fg_color="transparent",
            corner_radius=0,
        )
        self.program_details_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.program_details_frame.grid_columnconfigure(0, weight=1)

        self.status_bar = StatusBar(self.shell)
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def _sync_shell_width(self, _event: object | None = None) -> None:
        if not hasattr(self, "shell"):
            return

        try:
            if not self.shell.winfo_exists():
                return
            available_width = max(760, self.root.winfo_width() - 32)
            self.shell.configure(width=min(APP_CONTENT_MAX_WIDTH, available_width))
        except TclError:
            return

    def setup_protocols(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

    def _handle_close(self) -> None:
        close_behavior = self.config.get("close_behavior", "Minimize to Tray")
        if close_behavior == "Exit":
            if self.tray:
                self.tray.stop()
            self.root.destroy()
            return
        self.minimize_to_tray()

    def _get_presets(self) -> list[dict]:
        presets = self.config.get("presets", [])
        return [preset for preset in presets if isinstance(preset, dict)]

    def _get_filtered_presets(self) -> list[dict]:
        search_term = self._search_var.get().strip().lower()
        presets = self._get_presets()
        if not search_term:
            return presets

        filtered: list[dict] = []
        for preset in presets:
            search_parts = [str(preset.get("name", ""))]
            for index, program in enumerate(self._preset_programs(preset), start=1):
                search_parts.extend(
                    [
                        self._program_label(program, index),
                        str(program.get("executable_path", "")),
                        str(program.get("display_name", "")),
                    ]
                )
            searchable = " ".join(search_parts).lower()
            if search_term in searchable:
                filtered.append(preset)
        return filtered

    def _find_preset_by_name(self, name: str) -> dict | None:
        for preset in self._get_presets():
            if preset.get("name") == name:
                return preset
        return None

    def _program_label(self, program: dict, index: int) -> str:
        label = str(program.get("label", "")).strip()
        if label:
            return label

        executable_path = str(program.get("executable_path", "")).strip()
        if executable_path:
            return Path(executable_path).stem or f"Program {index}"
        return f"Program {index}"

    def _short_text(self, value: str, limit: int) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) <= limit:
            return cleaned
        return f"{cleaned[: max(0, limit - 3)].rstrip()}..."

    def _short_display_name(self, display_name: str) -> str:
        value = str(display_name).strip()
        if " - " in value:
            value = value.split(" - ", 1)[0]
        return self._short_text(value or "No display selected", 34)

    def _display_summary(self, programs: list[dict[str, str]]) -> str:
        displays: list[str] = []
        for program in programs:
            display_name = self._short_display_name(str(program.get("display_name", "")))
            if display_name and display_name not in displays:
                displays.append(display_name)

        if not displays:
            return "No display selected"
        if len(displays) == 1:
            return displays[0]
        return f"{displays[0]} + {len(displays) - 1} more"

    def _preset_programs(self, preset: dict) -> list[dict[str, str]]:
        return get_preset_programs(preset)

    def _preset_list_subtitle(self, preset: dict) -> str:
        programs = self._preset_programs(preset)
        if not programs:
            return "No programs configured"

        count_text = f"{len(programs)} program{'s' if len(programs) != 1 else ''}"
        display_summary = self._display_summary(programs)
        if display_summary == "No display selected":
            return count_text
        return f"{count_text} on {display_summary}"

    def _sync_notice_banner(self) -> None:
        if self._runtime_notices:
            self.notice_label.configure(text="\n".join(self._runtime_notices))
            self.notice_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))
        else:
            self.notice_frame.grid_forget()

    def _render_preset_list(self) -> None:
        for child in self.preset_list_frame.winfo_children():
            child.destroy()

        filtered_presets = self._get_filtered_presets()
        total_presets = len(self._get_presets())
        self.preset_count_label.configure(text=f"{total_presets} preset{'s' if total_presets != 1 else ''}")

        if not filtered_presets:
            empty_text = "No presets yet. Create a preset to launch and move an app."
            if self._search_var.get().strip():
                empty_text = "No presets match your search."

            empty_card = ctk.CTkFrame(self.preset_list_frame)
            style_card(empty_card, fg_color=SURFACE_ALT)
            empty_card.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
            ctk.CTkLabel(
                empty_card,
                text=empty_text,
                font=font(11),
                text_color=TEXT_MUTED,
                justify="left",
                wraplength=220,
            ).pack(fill="x", padx=10, pady=10)
            return

        for row_index, preset in enumerate(filtered_presets):
            name = str(preset.get("name", "Unnamed Preset"))
            subtitle = self._preset_list_subtitle(preset)
            selected = name == self._selected_preset_name
            fg_color = ("#e7efff", "#17294a") if selected else SURFACE_ALT
            hover_color = ("#dbe8ff", "#1d3763")
            border_color = ACCENT if selected else BORDER

            row_card = ctk.CTkFrame(self.preset_list_frame)
            style_card(row_card, fg_color=fg_color, border_color=border_color)
            row_card.grid(row=row_index, column=0, sticky="ew", padx=4, pady=3)
            row_card.grid_columnconfigure(1, weight=1)

            indicator = ctk.CTkFrame(
                row_card,
                width=3,
                height=44,
                fg_color=ACCENT if selected else "transparent",
                corner_radius=2,
            )
            indicator.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(9, 9), pady=10)

            title_label = ctk.CTkLabel(
                row_card,
                text=name,
                font=font(11, "bold"),
                anchor="w",
                justify="left",
                wraplength=245,
            )
            title_label.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(9, 0))

            subtitle_label = ctk.CTkLabel(
                row_card,
                text=subtitle,
                font=font(10),
                text_color=TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=245,
            )
            subtitle_label.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(1, 9))

            self._bind_preset_row(row_card, name, selected, fg_color, hover_color)

    def _bind_preset_row(
        self,
        row_card: ctk.CTkFrame,
        preset_name: str,
        selected: bool,
        fg_color: tuple[str, str],
        hover_color: tuple[str, str],
    ) -> None:
        def select_preset(_event: object | None = None) -> None:
            self._select_preset(preset_name)

        def show_hover(_event: object | None = None) -> None:
            if not selected:
                row_card.configure(fg_color=hover_color)

        def show_normal(_event: object | None = None) -> None:
            row_card.configure(fg_color=fg_color)

        row_card.bind("<Button-1>", select_preset)
        row_card.bind("<Enter>", show_hover)
        row_card.bind("<Leave>", show_normal)
        for child in row_card.winfo_children():
            child.bind("<Button-1>", select_preset)

    def _select_preset(self, preset_name: str) -> None:
        self._selected_preset_name = preset_name
        self._render_preset_list()
        self._render_details()

    def _render_details(self) -> None:
        preset = self._find_preset_by_name(self._selected_preset_name)
        has_preset = preset is not None

        if not has_preset:
            self.detail_title.configure(text="No preset selected")
            self.detail_subtitle.configure(
                text="Choose a preset on the left or create a compact app preset for your workflow."
            )
            self.detail_badge.configure(text="No preset")
            self._render_program_details([])
            self.run_btn.configure(state="disabled", fg_color=DISABLED, hover_color=DISABLED)
            self.edit_btn.configure(state="disabled")
            return

        self.detail_title.configure(text=str(preset.get("name", "Preset")))
        programs = self._preset_programs(preset)
        program_count = len(programs)
        self.detail_badge.configure(
            text=f"{program_count} program{'s' if program_count != 1 else ''}"
        )

        if programs:
            subtitle = (
                f"{program_count} program{'s' if program_count != 1 else ''} configured. "
                f"Targets: {self._display_summary(programs)}."
            )
        else:
            subtitle = "No programs are configured for this preset."
        self.detail_subtitle.configure(text=subtitle)

        self._render_program_details(programs)

        self.run_btn.configure(state="normal", fg_color=ACCENT, hover_color=ACCENT_HOVER)
        self.edit_btn.configure(state="normal")

    def _render_program_details(self, programs: list[dict[str, str]]) -> None:
        for child in self.program_details_frame.winfo_children():
            child.destroy()

        if not programs:
            empty_card = ctk.CTkFrame(self.program_details_frame)
            style_card(empty_card, fg_color=SURFACE_ALT)
            empty_card.grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(
                empty_card,
                text="No programs configured.",
                font=font(11, "bold"),
                text_color=TEXT_MUTED,
                anchor="w",
            ).pack(fill="x", padx=12, pady=12)
            return

        for index, program in enumerate(programs, start=1):
            card = ctk.CTkFrame(self.program_details_frame)
            style_card(card, fg_color=("#fbfcfe", "#151a20"))
            card.grid(row=index - 1, column=0, sticky="ew", pady=(0, 8))
            card.grid_columnconfigure(0, weight=1)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew", padx=12, pady=(9, 6))
            header.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                header,
                text=str(index),
                width=22,
                height=22,
                font=font(10, "bold"),
                fg_color=SURFACE_MUTED,
                corner_radius=11,
            ).grid(row=0, column=0, sticky="w", padx=(0, 8))

            ctk.CTkLabel(
                header,
                text=self._program_label(program, index),
                font=font(12, "bold"),
                anchor="w",
                justify="left",
                wraplength=360,
            ).grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(
                header,
                text=self._short_display_name(str(program.get("display_name", ""))),
                font=font(10, "bold"),
                fg_color=("#eef2f7", "#222b36"),
                text_color=TEXT_MUTED,
                corner_radius=999,
                padx=8,
                pady=3,
                anchor="e",
            ).grid(row=0, column=2, sticky="e", padx=(12, 0))

            fields = [
                ("Executable", str(program.get("executable_path", "")).strip() or "-"),
                (
                    "Arguments",
                    str(program.get("launch_args", "")).strip() or "No extra arguments",
                ),
                (
                    "Folder",
                    str(program.get("working_directory", "")).strip()
                    or "Uses executable folder automatically",
                ),
                (
                    "Hint",
                    str(program.get("window_title_hint", "")).strip()
                    or "Auto-detect by new window / process",
                ),
            ]
            field_grid = ctk.CTkFrame(card, fg_color="transparent")
            field_grid.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
            field_grid.grid_columnconfigure(1, weight=1)

            for field_row, (label, value) in enumerate(fields):
                ctk.CTkLabel(
                    field_grid,
                    text=label,
                    width=70,
                    font=font(10, "bold"),
                    text_color=TEXT_MUTED,
                    anchor="w",
                ).grid(row=field_row, column=0, sticky="nw", pady=(0, 2))
                ctk.CTkLabel(
                    field_grid,
                    text=value,
                    font=font(10),
                    anchor="w",
                    justify="left",
                    wraplength=610,
                ).grid(row=field_row, column=1, sticky="ew", pady=(0, 3))

    def minimize_to_tray(self) -> None:
        self.root.withdraw()

    def show_window(self) -> None:
        self.root.deiconify()
        self.root.focus_force()

    def run_preset(self) -> None:
        if not self._selected_preset_name:
            self.update_status("Select a preset first.", "error")
            return
        self.run_preset_by_name(self._selected_preset_name)

    def run_preset_by_name(self, name: str) -> bool:
        preset = self._find_preset_by_name(name)
        if not preset:
            self.update_status(f"Preset '{name}' not found.", "error")
            return False

        self._selected_preset_name = name
        self._render_preset_list()
        self._render_details()

        def reporter(status_type: str, message: str) -> None:
            self.update_status(message, status_type)

        return execute_preset(preset, reporter=reporter)

    def new_preset(self) -> None:
        self.update_status("Creating a new preset...", "info")
        self._open_preset_form(preset=None)

    def edit_preset(self) -> None:
        if not self._selected_preset_name:
            self.update_status("Select a preset to edit.", "error")
            return

        preset = self._find_preset_by_name(self._selected_preset_name)
        if not preset:
            self.update_status(f"Preset '{self._selected_preset_name}' not found.", "error")
            return

        self.update_status(f"Editing preset '{self._selected_preset_name}'...", "info")
        self._open_preset_form(preset=preset)

    def _open_preset_form(self, preset: dict | None) -> None:
        is_edit = preset is not None
        action_state = {"action": "cancelled"}

        def on_preset_saved(saved_preset: dict | None) -> None:
            action_state["action"] = "saved" if saved_preset else "deleted"
            self._reload_presets(selected_name=saved_preset.get("name") if saved_preset else "")
            if self.tray:
                self.tray.update_menu()

            if saved_preset and saved_preset.get("name"):
                status_action = "updated" if is_edit else "created"
                self.update_status(f"Preset '{saved_preset['name']}' {status_action}.", "ready")
            elif preset and preset.get("name"):
                self.update_status(f"Preset '{preset['name']}' deleted.", "ready")
            else:
                self.update_status("Preset list updated.", "ready")

        form = PresetForm(self.root, preset=preset, on_save=on_preset_saved)
        form.window.wait_window()

        if action_state["action"] == "cancelled":
            self.update_status(
                "Preset edit cancelled." if is_edit else "Preset creation cancelled.",
                "info",
            )

    def open_settings(self) -> None:
        self.update_status("Opening settings...", "info")

        def on_settings_applied(_settings: dict) -> None:
            self._reload_presets(selected_name=self._selected_preset_name)
            self.update_status("Settings applied.", "ready")

        SettingsWindow(
            self.root,
            on_apply=on_settings_applied,
            preset_names=[preset.get("name", "") for preset in self._get_presets()],
            selected_preset=self._selected_preset_name,
        )

    def update_status(self, message: str, status_type: str = "ready") -> None:
        self.status_bar.set_status(status_type, message)
        self.root.update_idletasks()

    def _reload_presets(self, selected_name: str | None = None, initial: bool = False) -> None:
        previous_selection = selected_name or self._selected_preset_name
        self.config = load_config()
        self._runtime_notices = consume_runtime_notices()
        apply_base_theme(self.config.get("theme", "System"))
        self.root.configure(fg_color=SURFACE)

        presets = self._get_presets()
        preset_names = [str(preset.get("name", "")) for preset in presets if preset.get("name")]

        if previous_selection and previous_selection in preset_names:
            self._selected_preset_name = previous_selection
        elif preset_names:
            self._selected_preset_name = preset_names[0]
        else:
            self._selected_preset_name = ""

        self._sync_notice_banner()
        self._render_preset_list()
        self._render_details()

        if initial:
            if self._runtime_notices:
                self.update_status(self._runtime_notices[0], "info")
            else:
                self.update_status("Ready to launch and move apps.", "ready")
