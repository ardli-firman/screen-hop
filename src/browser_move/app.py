"""Main window UI for ScreenHop."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from src.browser_move import APP_NAME, __version__
from src.browser_move.config import consume_runtime_notices, load_config
from src.browser_move.preset_form import PresetForm
from src.browser_move.preset_runner import execute_preset
from src.browser_move.settings_window import SettingsWindow
from src.browser_move.status_bar import StatusBar
from src.browser_move.ui_theme import (
    ACCENT,
    ACCENT_HOVER,
    APP_GEOMETRY,
    APP_MIN_SIZE,
    BORDER,
    INFO,
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

        shell = ctk.CTkFrame(self.root, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        shell.grid_columnconfigure(0, weight=0)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(shell, width=320)
        style_panel(self.sidebar)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=1)

        sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        sidebar_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar_header,
            text=APP_NAME,
            font=font(24, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            sidebar_header,
            text=f"v{__version__}",
            font=font(10, "bold"),
            text_color=TEXT_MUTED,
            anchor="e",
        ).grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            sidebar_header,
            text="Launch any Windows app and snap it to the right display.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=252,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self.notice_frame = ctk.CTkFrame(self.sidebar)
        style_card(self.notice_frame, fg_color=("#fff4e5", "#3a2a0e"), border_color=WARN)
        self.notice_label = ctk.CTkLabel(
            self.notice_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=250,
            font=font(11, "bold"),
        )
        self.notice_label.pack(fill="x", padx=12, pady=10)

        sidebar_actions = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        sidebar_actions.grid_columnconfigure(0, weight=1)

        self.new_btn = ctk.CTkButton(
            sidebar_actions,
            text="New Preset",
            command=self.new_preset,
            height=42,
            corner_radius=14,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(13, "bold"),
        )
        self.new_btn.grid(row=0, column=0, sticky="ew")

        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            textvariable=self._search_var,
            height=40,
            corner_radius=14,
            placeholder_text="Search presets...",
            border_color=BORDER,
        )
        self.search_entry.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 8))
        self._search_var.trace_add("write", lambda *_args: self._render_preset_list())

        self.preset_count_label = ctk.CTkLabel(
            self.sidebar,
            text="0 presets",
            font=font(11, "bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.preset_count_label.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 8))

        self.preset_list_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0,
        )
        self.preset_list_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.preset_list_frame.grid_columnconfigure(0, weight=1)

        content = ctk.CTkFrame(shell, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        header_card = ctk.CTkFrame(content)
        style_panel(header_card)
        header_card.grid(row=0, column=0, sticky="ew")
        header_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_card,
            text="Preset Control Panel",
            font=font(22, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(
            header_card,
            text="Keep launch, move, and shortcut workflows in one compact view.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

        self.hero_card = ctk.CTkFrame(content)
        style_panel(self.hero_card)
        self.hero_card.grid(row=1, column=0, sticky="ew", pady=(16, 16))
        self.hero_card.grid_columnconfigure(0, weight=1)
        self.hero_card.grid_columnconfigure(1, weight=0)

        hero_text = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_text.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        hero_text.grid_columnconfigure(0, weight=1)

        self.detail_title = ctk.CTkLabel(
            hero_text,
            text="No preset selected",
            font=font(20, "bold"),
            anchor="w",
        )
        self.detail_title.grid(row=0, column=0, sticky="w")

        self.detail_subtitle = ctk.CTkLabel(
            hero_text,
            text="Choose a preset on the left or create a new one.",
            font=font(12),
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=460,
        )
        self.detail_subtitle.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        action_stack = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        action_stack.grid(row=0, column=1, sticky="ns", padx=(0, 20), pady=20)

        self.run_btn = ctk.CTkButton(
            action_stack,
            text="Launch & Move",
            command=self.run_preset,
            width=180,
            height=46,
            corner_radius=14,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=font(14, "bold"),
        )
        self.run_btn.pack(fill="x")

        self.edit_btn = ctk.CTkButton(
            action_stack,
            text="Edit Preset",
            command=self.edit_preset,
            width=180,
            height=40,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE_MUTED,
            border_width=1,
            border_color=BORDER,
            font=font(13, "bold"),
        )
        self.edit_btn.pack(fill="x", pady=(10, 8))

        self.settings_btn = ctk.CTkButton(
            action_stack,
            text="Settings",
            command=self.open_settings,
            width=180,
            height=40,
            corner_radius=14,
            fg_color=SURFACE_ALT,
            hover_color=SURFACE_MUTED,
            border_width=1,
            border_color=BORDER,
            font=font(13, "bold"),
        )
        self.settings_btn.pack(fill="x")

        self.details_card = ctk.CTkFrame(content)
        style_panel(self.details_card)
        self.details_card.grid(row=2, column=0, sticky="nsew")
        self.details_card.grid_columnconfigure(0, weight=1)

        details_header = ctk.CTkFrame(self.details_card, fg_color="transparent")
        details_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        details_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            details_header,
            text="Preset Details",
            font=font(16, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.detail_badge = ctk.CTkLabel(
            details_header,
            text="Universal app preset",
            font=font(11, "bold"),
            fg_color=("#e4f0ff", "#1a2f52"),
            text_color=INFO,
            corner_radius=999,
            padx=12,
            pady=5,
        )
        self.detail_badge.grid(row=0, column=1, sticky="e")

        self.details_grid = ctk.CTkFrame(self.details_card, fg_color="transparent")
        self.details_grid.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.details_grid.grid_columnconfigure(0, weight=1)

        self.detail_rows: dict[str, ctk.CTkLabel] = {}
        detail_specs = [
            ("Executable", "executable_path"),
            ("Arguments", "launch_args"),
            ("Working Folder", "working_directory"),
            ("Window Hint", "window_title_hint"),
            ("Target Display", "display_name"),
        ]
        for index, (label_text, key) in enumerate(detail_specs):
            row = ctk.CTkFrame(self.details_grid)
            style_card(row, corner_radius=16)
            row.grid(row=index, column=0, sticky="ew", pady=(0, 10))
            row.grid_columnconfigure(0, weight=0)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=label_text,
                font=font(11, "bold"),
                text_color=TEXT_MUTED,
                anchor="w",
            ).grid(row=0, column=0, sticky="nw", padx=(14, 12), pady=14)

            value_label = ctk.CTkLabel(
                row,
                text="-",
                font=font(12, "bold"),
                anchor="w",
                justify="left",
                wraplength=520,
            )
            value_label.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=14)
            self.detail_rows[key] = value_label

        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

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
            searchable = " ".join(
                [
                    str(preset.get("name", "")),
                    str(preset.get("executable_path", "")),
                    str(preset.get("display_name", "")),
                ]
            ).lower()
            if search_term in searchable:
                filtered.append(preset)
        return filtered

    def _find_preset_by_name(self, name: str) -> dict | None:
        for preset in self._get_presets():
            if preset.get("name") == name:
                return preset
        return None

    def _sync_notice_banner(self) -> None:
        if self._runtime_notices:
            self.notice_label.configure(text="\n".join(self._runtime_notices))
            self.notice_frame.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))
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
                font=font(12),
                text_color=TEXT_MUTED,
                justify="left",
                wraplength=240,
            ).pack(fill="x", padx=14, pady=14)
            return

        for row_index, preset in enumerate(filtered_presets):
            name = str(preset.get("name", "Unnamed Preset"))
            display_name = str(preset.get("display_name", "No display selected"))
            selected = name == self._selected_preset_name
            fg_color = ("#ddf6ef", "#143129") if selected else SURFACE_ALT
            border_color = ACCENT if selected else BORDER

            row_button = ctk.CTkButton(
                self.preset_list_frame,
                text=f"{name}\n{display_name}",
                command=lambda preset_name=name: self._select_preset(preset_name),
                height=68,
                corner_radius=16,
                anchor="w",
                fg_color=fg_color,
                hover_color=("#cdeee4", "#1d4438"),
                border_width=1,
                border_color=border_color,
                font=font(12, "bold"),
            )
            row_button.grid(row=row_index, column=0, sticky="ew", padx=4, pady=4)

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
            for label in self.detail_rows.values():
                label.configure(text="-")
            self.run_btn.configure(state="disabled", fg_color=("#b7c8c2", "#26443b"), hover_color=("#b7c8c2", "#26443b"))
            self.edit_btn.configure(state="disabled")
            return

        self.detail_title.configure(text=str(preset.get("name", "Preset")))
        subtitle = str(preset.get("display_name", "No display selected"))
        title_hint = str(preset.get("window_title_hint", "")).strip()
        if title_hint:
            subtitle = f"Moves new window to {subtitle}. Title hint: {title_hint}"
        else:
            subtitle = f"Moves new window to {subtitle}."
        self.detail_subtitle.configure(text=subtitle)

        values = {
            "executable_path": str(preset.get("executable_path", "-")) or "-",
            "launch_args": str(preset.get("launch_args", "")).strip() or "No extra arguments",
            "working_directory": str(preset.get("working_directory", "")).strip() or "Uses executable folder automatically",
            "window_title_hint": title_hint or "Auto-detect by new window / process",
            "display_name": str(preset.get("display_name", "-")) or "-",
        }
        for key, label in self.detail_rows.items():
            label.configure(text=values.get(key, "-"))

        self.run_btn.configure(state="normal", fg_color=ACCENT, hover_color=ACCENT_HOVER)
        self.edit_btn.configure(state="normal")

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
