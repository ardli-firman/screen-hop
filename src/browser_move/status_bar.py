"""Status bar component for ScreenHop."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import customtkinter as ctk

from src.browser_move.ui_theme import BORDER, CORNER_RADIUS, SURFACE_ALT, TEXT_MUTED, font, status_color

StatusType = Literal["ready", "running", "error", "info"]


class StatusBar(ctk.CTkFrame):
    """Compact status bar showing current state with a timestamp."""

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
        super().__init__(master, height=38, **kwargs)
        self.pack_propagate(False)
        self.configure(
            fg_color=SURFACE_ALT,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=BORDER,
        )

        self._status_type: StatusType = "ready"
        self._message = "Ready"

        self._setup_ui()
        self.set_status("ready", "Ready")

    def _setup_ui(self) -> None:
        self.indicator = ctk.CTkLabel(
            self,
            text="",
            width=8,
            height=8,
            corner_radius=4,
        )
        self.indicator.pack(side="left", padx=(12, 8))

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=font(11, "bold"),
            anchor="w",
        )
        self.status_label.pack(side="left", fill="both", expand=True)

        self.time_label = ctk.CTkLabel(
            self,
            text="",
            font=font(11),
            text_color=TEXT_MUTED,
            anchor="e",
        )
        self.time_label.pack(side="right", padx=(8, 12))

    def set_status(self, status_type: StatusType, message: str) -> None:
        self._status_type = status_type
        self._message = message
        self.indicator.configure(fg_color=status_color(status_type))
        self.status_label.configure(text=message)
        self.time_label.configure(text=datetime.now().strftime("%H:%M:%S"))

    def set_status_threadsafe(self, root: ctk.CTk, status_type: StatusType, message: str) -> None:
        root.after(0, lambda: self.set_status(status_type, message))

    def clear(self) -> None:
        self.set_status("ready", "Ready")

    def get_status(self) -> tuple[StatusType, str]:
        return self._status_type, self._message
