"""Status bar component for browser move automation."""

from __future__ import annotations

import customtkinter as ctk
from datetime import datetime
from typing import Literal


class StatusBar(ctk.CTkFrame):
    """Status bar component showing current status with color indicator."""

    STATUS_COLORS = {
        "ready": "#2ecc71",
        "running": "#f39c12",
        "error": "#e74c3c",
    }

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
        """Initialize status bar.

        Args:
            master: Parent widget
            **kwargs: Additional kwargs passed to CTkFrame
        """
        super().__init__(master, height=40, **kwargs)
        self.pack_propagate(False)

        self._status_type: Literal["ready", "running", "error"] = "ready"
        self._message: str = "Ready"

        self._setup_ui()
        self.set_status("ready", "Ready")

    def _setup_ui(self) -> None:
        # Indicator dot
        self.indicator = ctk.CTkLabel(
            self,
            text="",
            width=12,
            height=12,
            fg_color=self.STATUS_COLORS["ready"],
            corner_radius=6,
        )
        self.indicator.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_label.pack(side="left", padx=5, fill="both", expand=True)

        self.time_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="e",
        )
        self.time_label.pack(side="right", padx=10)

    def set_status(
        self,
        status_type: Literal["ready", "running", "error"],
        message: str,
    ) -> None:
        """Update status bar with new status type and message.

        Args:
            status_type: One of "ready", "running", "error"
            message: Status message to display
        """
        self._status_type = status_type
        self._message = message

        color = self.STATUS_COLORS.get(status_type, "#95a5a6")
        self.indicator.configure(fg_color=color)

        self.status_label.configure(text=message)

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=timestamp)

    def set_status_threadsafe(
        self,
        root: ctk.CTk,
        status_type: Literal["ready", "running", "error"],
        message: str,
    ) -> None:
        """Thread-safe status update using root.after.

        Args:
            root: CTk root window for after() scheduling
            status_type: One of "ready", "running", "error"
            message: Status message to display
        """

        def update():
            self.set_status(status_type, message)

        root.after(0, update)

    def clear(self) -> None:
        """Reset status bar to ready state."""
        self.set_status("ready", "Ready")

    def get_status(self) -> tuple[Literal["ready", "running", "error"], str]:
        """Get current status type and message.

        Returns:
            Tuple of (status_type, message)
        """
        return (self._status_type, self._message)
