"""Preset management form UI for browser_move."""

import re
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable
from src.browser_move.config import load_config, save_config
from src.browser_move.browsers import detect_browser_path
from src.browser_move.monitors import get_monitor_choices


class PresetForm:
    """Modal form for adding/editing browser presets."""

    def __init__(
        self,
        parent: ctk.CTk,
        preset: dict | None = None,
        on_save: Callable | None = None,
    ):
        """Initialize preset form.

        Args:
            parent: Parent window (CTk or CTkToplevel)
            preset: Existing preset dict for edit mode, None for add mode
            on_save: Callback function to call after successful save
        """
        self.parent = parent
        self.preset = preset
        self.on_save = on_save
        self.result = None
        self._monitor_id_by_label: dict[str, str] = {}
        self._monitor_label_by_id: dict[str, str] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Create the modal form UI."""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Add Preset" if not self.preset else "Edit Preset")
        self.window.geometry("540x620")
        self.window.minsize(500, 560)
        self.window.resizable(True, True)
        self.window.grab_set()
        self.window.transient(self.parent)
        self._center_window()

        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            main_frame,
            text="Add New Preset" if not self.preset else "Edit Preset",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.pack(fill="x", pady=(0, 10))

        # Scrollable body prevents action buttons from being clipped on high-DPI displays.
        form_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        name_label = ctk.CTkLabel(
            form_frame,
            text="Preset Name *",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        name_label.pack(fill="x", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            font=ctk.CTkFont(size=13),
            placeholder_text="Enter preset name",
        )
        self.name_entry.pack(fill="x", pady=(0, 15))

        browser_label = ctk.CTkLabel(
            form_frame,
            text="Browser Type *",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        browser_label.pack(fill="x", pady=(0, 5))

        self.browser_combo = ctk.CTkComboBox(
            form_frame,
            values=["firefox", "chrome", "edge"],
            height=40,
            font=ctk.CTkFont(size=13),
            state="readonly",
        )
        self.browser_combo.pack(fill="x", pady=(0, 15))
        self.browser_combo.set("firefox")

        monitor_label = ctk.CTkLabel(
            form_frame,
            text="Target Monitor *",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        monitor_label.pack(fill="x", pady=(0, 5))

        monitor_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        monitor_row.pack(fill="x", pady=(0, 15))

        self.monitor_combo = ctk.CTkComboBox(
            monitor_row,
            values=["Loading monitors..."],
            height=40,
            font=ctk.CTkFont(size=13),
            state="readonly",
        )
        self.monitor_combo.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.refresh_monitors_btn = ctk.CTkButton(
            monitor_row,
            text="Refresh",
            width=90,
            height=40,
            command=self.refresh_monitor_choices,
        )
        self.refresh_monitors_btn.pack(side="right")

        self.refresh_monitor_choices()

        url_label = ctk.CTkLabel(
            form_frame,
            text="URL *",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        url_label.pack(fill="x", pady=(0, 5))

        self.url_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            font=ctk.CTkFont(size=13),
            placeholder_text="https://example.com",
        )
        self.url_entry.pack(fill="x", pady=(0, 15))

        path_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=(0, 15))

        path_label = ctk.CTkLabel(
            path_frame,
            text="Browser Path (optional)",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        path_label.pack(fill="x", pady=(0, 5))

        path_entry_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_entry_frame.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            path_entry_frame,
            height=40,
            font=ctk.CTkFont(size=13),
            placeholder_text="Leave empty for auto-detect",
        )
        self.path_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.detect_btn = ctk.CTkButton(
            path_entry_frame,
            text="Auto-Detect",
            width=110,
            height=40,
            command=self.auto_detect_path,
        )
        self.detect_btn.pack(side="right")

        self.kiosk_var = ctk.BooleanVar(value=False)
        self.kiosk_checkbox = ctk.CTkCheckBox(
            form_frame,
            text="Kiosk Mode (Fullscreen)",
            variable=self.kiosk_var,
            font=ctk.CTkFont(size=13),
            checkbox_width=20,
            checkbox_height=20,
        )
        self.kiosk_checkbox.pack(fill="x", pady=(10, 0))

        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))

        button_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        if self.preset:
            self.save_btn = ctk.CTkButton(
                button_frame,
                text="Update",
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.save_preset,
            )
            self.save_btn.pack(side="left", fill="both", expand=True, padx=(0, 10))

            self.delete_btn = ctk.CTkButton(
                button_frame,
                text="Delete",
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="#dc3545",
                hover_color="#c82333",
                command=self.delete_preset,
            )
            self.delete_btn.pack(side="right", padx=(10, 0))
        else:
            self.save_btn = ctk.CTkButton(
                button_frame,
                text="Save",
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.save_preset,
            )
            self.save_btn.pack(fill="x")

        self.cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancel",
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            border_width=2,
            command=self.window.destroy,
        )
        self.cancel_btn.pack(fill="x", pady=(10, 0))

        if self.preset:
            self._populate_fields()

    def _center_window(self) -> None:
        """Center the modal window over parent."""
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        window_width = 540
        window_height = 620

        if parent_width <= 1 or parent_height <= 1:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        else:
            x = parent_x + (parent_width - window_width) // 2
            y = parent_y + (parent_height - window_height) // 2

        x = max(0, x)
        y = max(0, y)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _populate_fields(self) -> None:
        """Fill form fields with existing preset data."""
        self.name_entry.insert(0, self.preset.get("name", ""))
        self.browser_combo.set(self.preset.get("browser_type", "firefox"))
        self.url_entry.insert(0, self.preset.get("url", ""))
        self.path_entry.insert(0, self.preset.get("browser_path", ""))
        self.kiosk_var.set(self.preset.get("kiosk_mode", False))

        saved_monitor_id = str(self.preset.get("monitor_id", "") or "").strip()
        saved_monitor_name = str(self.preset.get("monitor_name", "") or "").strip()

        if saved_monitor_id and saved_monitor_id in self._monitor_label_by_id:
            self.monitor_combo.set(self._monitor_label_by_id[saved_monitor_id])
            return

        if saved_monitor_name and saved_monitor_name in self._monitor_id_by_label:
            self.monitor_combo.set(saved_monitor_name)

    def refresh_monitor_choices(self) -> None:
        """Reload monitor list from system and refresh monitor dropdown."""
        current_label = self.monitor_combo.get() if hasattr(self, "monitor_combo") else ""

        self._monitor_id_by_label.clear()
        self._monitor_label_by_id.clear()

        choices = get_monitor_choices()
        if not choices:
            self.monitor_combo.configure(values=["No monitor detected"], state="disabled")
            self.monitor_combo.set("No monitor detected")
            return

        labels: list[str] = []
        for monitor_id, label in choices:
            labels.append(label)
            self._monitor_id_by_label[label] = monitor_id
            self._monitor_label_by_id[monitor_id] = label

        self.monitor_combo.configure(values=labels, state="readonly")
        if current_label in self._monitor_id_by_label:
            self.monitor_combo.set(current_label)
        else:
            self.monitor_combo.set(labels[0])

    def auto_detect_path(self) -> None:
        browser_type = self.browser_combo.get()
        detected_path = detect_browser_path(browser_type)

        if detected_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, detected_path)
        else:
            self.show_error(f"Could not find {browser_type} installation")

    def validate_url(self, url: str) -> bool:
        """Validate URL format.

        Args:
            url: URL string to validate

        Returns:
            True if valid http/https URL, False otherwise
        """
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return re.match(pattern, url) is not None

    def validate_form(self) -> tuple[bool, str]:
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        selected_monitor = self.monitor_combo.get().strip()

        if not name:
            return False, "Preset name is required"

        config = load_config()
        presets = config.get("presets", [])

        for preset in presets:
            if preset["name"].lower() == name.lower():
                if self.preset and self.preset["name"] == preset["name"]:
                    continue
                return False, f"Preset name '{name}' already exists"

        if not url:
            return False, "URL is required"

        if not self.validate_url(url):
            return False, "URL must start with http:// or https://"

        if selected_monitor not in self._monitor_id_by_label:
            return False, "Please select a valid monitor target"

        return True, ""

    def save_preset(self) -> None:
        is_valid, error_msg = self.validate_form()

        if not is_valid:
            self.show_error(error_msg)
            return

        preset_data = {
            "name": self.name_entry.get().strip(),
            "browser_type": self.browser_combo.get(),
            "browser_path": self.path_entry.get().strip(),
            "url": self.url_entry.get().strip(),
            "kiosk_mode": self.kiosk_var.get(),
            "monitor_id": self._monitor_id_by_label[self.monitor_combo.get().strip()],
            "monitor_name": self.monitor_combo.get().strip(),
        }

        config = load_config()
        presets = config.get("presets", [])

        if self.preset:
            for i, existing in enumerate(presets):
                if existing["name"] == self.preset["name"]:
                    presets[i] = preset_data
                    self.show_success(f"Preset '{preset_data['name']}' updated")
                    break
        else:
            presets.append(preset_data)
            self.show_success(f"Preset '{preset_data['name']}' created")

        config["presets"] = presets

        if save_config(config):
            self.result = preset_data
            if self.on_save:
                self.on_save(preset_data)
            self.window.destroy()
        else:
            self.show_error("Failed to save configuration")

    def delete_preset(self) -> None:
        if not self.preset:
            return

        confirm = messagebox.askyesno(
            title="Confirm Delete",
            message=f"Are you sure you want to delete preset '{self.preset['name']}'?",
        )

        if not confirm:
            return

        config = load_config()
        presets = config.get("presets", [])

        presets = [p for p in presets if p["name"] != self.preset["name"]]
        config["presets"] = presets

        if save_config(config):
            self.show_success(f"Preset '{self.preset['name']}' deleted")
            if self.on_save:
                self.on_save(None)
            self.window.destroy()
        else:
            self.show_error("Failed to delete preset")

    def show_error(self, message: str) -> None:
        """Show error message dialog."""
        messagebox.showerror("Error", message)

    def show_success(self, message: str) -> None:
        print(f"[preset_form] {message}")
