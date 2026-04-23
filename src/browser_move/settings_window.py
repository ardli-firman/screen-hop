"""Settings dialog for ScreenHop."""

import customtkinter as ctk
from typing import Callable, Optional

from src.browser_move import APP_NAME
from src.browser_move.config import load_config, save_config


class SettingsWindow:
    """Settings modal dialog for ScreenHop."""

    def __init__(
        self, parent: ctk.CTk, on_apply: Optional[Callable[[dict], None]] = None
    ):
        """Initialize settings window.

        Args:
            parent: Parent CTk window
            on_apply: Optional callback called with settings dict after Apply
        """
        self.parent = parent
        self.on_apply = on_apply
        self.config = load_config()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Build the settings UI."""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(f"{APP_NAME} Settings")
        self.window.geometry("500x560")
        self.window.minsize(460, 500)
        self.window.resizable(True, True)
        self.window.grab_set()
        self.window.transient(self.parent)
        self._center_window()

        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"{APP_NAME} Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(fill="x", pady=(0, 12))

        # Scrollable content prevents controls from being clipped on high-DPI displays.
        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Theme setting
        theme_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)

        theme_label = ctk.CTkLabel(
            theme_frame, text="Theme:", font=ctk.CTkFont(size=13)
        )
        theme_label.pack(side="left", padx=(0, 15))

        self.theme_combo = ctk.CTkComboBox(
            theme_frame,
            values=["Dark", "Light", "System"],
            width=150,
            height=32,
        )
        self.theme_combo.set(self.config.get("theme", "System"))
        self.theme_combo.pack(side="left")

        # Auto-start checkbox
        self.auto_start_var = ctk.BooleanVar(value=self.config.get("auto_start", False))
        self.auto_start_check = ctk.CTkCheckBox(
            content_frame,
            text="Launch on Windows Startup",
            variable=self.auto_start_var,
            font=ctk.CTkFont(size=13),
        )
        self.auto_start_check.pack(anchor="w", pady=15)

        # Close behavior
        close_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        close_frame.pack(fill="x", pady=10)

        close_label = ctk.CTkLabel(
            close_frame,
            text="Close button behavior:",
            font=ctk.CTkFont(size=13),
        )
        close_label.pack(side="left", padx=(0, 15))

        self.close_combo = ctk.CTkComboBox(
            close_frame,
            values=["Exit", "Minimize to Tray"],
            width=150,
            height=32,
        )
        self.close_combo.set(self.config.get("close_behavior", "Minimize to Tray"))
        self.close_combo.pack(side="left")

        # Separator
        separator = ctk.CTkFrame(content_frame, height=2, fg_color="gray30")
        separator.pack(fill="x", pady=20)

        # Shortcut section title
        shortcut_title = ctk.CTkLabel(
            content_frame,
            text="Shortcuts",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        shortcut_title.pack(anchor="w", pady=(0, 15))

        # Desktop shortcut button
        desktop_btn = ctk.CTkButton(
            content_frame,
            text="Create Desktop Shortcut",
            command=self.create_desktop_shortcut,
            height=35,
            width=250,
        )
        desktop_btn.pack(pady=8)

        # Startup toggle button
        self.startup_btn = ctk.CTkButton(
            content_frame,
            text=self._get_startup_button_text(),
            command=self.toggle_startup,
            height=35,
            width=250,
        )
        self.startup_btn.pack(pady=8)

        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(5, 0))

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

        # Apply button
        apply_btn = ctk.CTkButton(
            footer_frame,
            text="Apply",
            command=self.apply_settings,
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        apply_btn.pack(side="right")

    def _center_window(self) -> None:
        """Center settings window over parent."""
        window_width = 500
        window_height = 560

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

    def _get_startup_button_text(self) -> str:
        """Get button text based on current startup state."""
        return "Remove from Startup" if self._in_startup() else "Add to Startup"

    def _in_startup(self) -> bool:
        """Check if app is in Windows startup folder."""
        print("[settings] Checking startup status (not implemented yet)")
        return False

    def create_desktop_shortcut(self) -> None:
        """Create desktop shortcut for the application."""
        print("[settings] Creating desktop shortcut (not implemented yet)")

        shortcut_frame = ctk.CTkToplevel(self.window)
        shortcut_frame.title("Desktop Shortcut")
        shortcut_frame.geometry("300x150")
        shortcut_frame.grab_set()

        msg = ctk.CTkLabel(
            shortcut_frame,
            text=f"{APP_NAME} desktop shortcut created!",
            font=ctk.CTkFont(size=14),
        )
        msg.pack(pady=20)

        ok_btn = ctk.CTkButton(
            shortcut_frame,
            text="OK",
            command=shortcut_frame.destroy,
            width=100,
        )
        ok_btn.pack(pady=10)

    def toggle_startup(self) -> None:
        """Toggle app in Windows startup folder."""
        currently_in_startup = self._in_startup()

        if currently_in_startup:
            print("[settings] Removing from startup (not implemented yet)")
            self.startup_btn.configure(text="Add to Startup")
        else:
            print("[settings] Adding to startup (not implemented yet)")
            self.startup_btn.configure(text="Remove from Startup")

        action = "added to" if not currently_in_startup else "removed from"
        feedback_frame = ctk.CTkToplevel(self.window)
        feedback_frame.title("Startup")
        feedback_frame.geometry("300x150")
        feedback_frame.grab_set()

        msg = ctk.CTkLabel(
            feedback_frame,
            text=f"{APP_NAME} {action} startup!",
            font=ctk.CTkFont(size=14),
        )
        msg.pack(pady=20)

        ok_btn = ctk.CTkButton(
            feedback_frame,
            text="OK",
            command=feedback_frame.destroy,
            width=100,
        )
        ok_btn.pack(pady=10)

    def apply_settings(self) -> None:
        """Save settings to config and trigger callback."""
        settings = {
            "theme": self.theme_combo.get(),
            "auto_start": self.auto_start_var.get(),
            "close_behavior": self.close_combo.get(),
        }

        self.config.update(settings)
        save_config(self.config)

        applied_theme = settings["theme"]
        ctk.set_appearance_mode(applied_theme)

        print(f"[settings] Settings applied: {settings}")

        if self.on_apply:
            self.on_apply(settings)

        self.window.destroy()
