"""Built-in preset templates for ScreenHop."""

from __future__ import annotations

from pathlib import Path

from src.browser_move.browsers import BROWSER_PATHS, detect_browser_path

DEFAULT_FIREFOX_KIOSK_URL = "http://172.16.61.60:1999/antrian-poli"


def get_template_choices() -> list[tuple[str, str]]:
    """Return available built-in preset template choices."""
    return [
        ("blank", "Blank / Manual"),
        ("browser_kiosk_firefox", "Browser Kiosk (Firefox)"),
    ]


def build_preset_template(template_id: str) -> dict[str, str]:
    """Build preset field values for a built-in template."""
    normalized = str(template_id or "").strip().lower()
    if normalized == "browser_kiosk_firefox":
        executable_path = detect_browser_path("firefox") or BROWSER_PATHS["firefox"][0]
        working_directory = ""
        if executable_path:
            working_directory = str(Path(executable_path).parent)

        return {
            "name": "Firefox Kiosk",
            "executable_path": executable_path,
            "launch_args": f'--new-window --kiosk="{DEFAULT_FIREFOX_KIOSK_URL}"',
            "working_directory": working_directory,
            "window_title_hint": "Firefox",
            "_template_notice": (
                "Firefox kiosk template applied from docs/run.bat. "
                "Adjust the URL or executable path if needed."
            ),
        }

    return {}
