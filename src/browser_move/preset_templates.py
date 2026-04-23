"""Built-in preset templates for ScreenHop."""

from __future__ import annotations

from pathlib import Path

from src.browser_move.browsers import BROWSER_PATHS, detect_browser_path

DEFAULT_FIREFOX_KIOSK_URL = "http://172.16.61.60:1999/antrian-poli"
DEFAULT_BROWSER_URL = "https://example.com"
DEFAULT_NOTEPAD_PATH = r"C:\Windows\System32\notepad.exe"

APP_PATHS: dict[str, list[str]] = {
    "vlc": [
        "C:/Program Files/VideoLAN/VLC/vlc.exe",
        "C:/Program Files (x86)/VideoLAN/VLC/vlc.exe",
    ],
    "obs": [
        "C:/Program Files/obs-studio/bin/64bit/obs64.exe",
        "C:/Program Files/obs-studio/bin/32bit/obs32.exe",
    ],
    "notepad": [DEFAULT_NOTEPAD_PATH],
}

BROWSER_TITLE_HINTS = {
    "firefox": "Firefox",
    "chrome": "Chrome",
    "edge": "Microsoft Edge",
}


def _resolve_path(candidates: list[str]) -> str:
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
    return candidates[0] if candidates else ""


def _resolve_browser_path(browser_type: str) -> str:
    return detect_browser_path(browser_type) or _resolve_path(BROWSER_PATHS.get(browser_type, []))


def _resolve_app_path(app_type: str) -> str:
    return _resolve_path(APP_PATHS.get(app_type, []))


def _build_browser_template(browser_type: str, kiosk_mode: bool) -> dict[str, str]:
    executable_path = _resolve_browser_path(browser_type)
    working_directory = str(Path(executable_path).parent) if executable_path else ""
    title_hint = BROWSER_TITLE_HINTS.get(browser_type, browser_type.title())
    browser_name = title_hint

    if browser_type == "firefox":
        if kiosk_mode:
            launch_args = f'--new-window --kiosk="{DEFAULT_FIREFOX_KIOSK_URL}"'
            name = "Firefox Kiosk"
        else:
            launch_args = f"--new-window {DEFAULT_BROWSER_URL}"
            name = "Firefox Window"
    elif browser_type == "chrome":
        if kiosk_mode:
            launch_args = f'--kiosk --app="{DEFAULT_BROWSER_URL}"'
            name = "Chrome Kiosk"
        else:
            launch_args = f"--new-window {DEFAULT_BROWSER_URL}"
            name = "Chrome Window"
    elif browser_type == "edge":
        if kiosk_mode:
            launch_args = f"--kiosk {DEFAULT_BROWSER_URL}"
            name = "Edge Kiosk"
        else:
            launch_args = DEFAULT_BROWSER_URL
            name = "Edge Window"
    else:
        return {}

    usage = "kiosk" if kiosk_mode else "window"
    return {
        "name": name,
        "executable_path": executable_path,
        "launch_args": launch_args,
        "working_directory": working_directory,
        "window_title_hint": title_hint,
        "_template_notice": (
            f"{browser_name} {usage} template applied. "
            "Adjust the URL or executable path if needed."
        ),
    }


def get_template_choices() -> list[tuple[str, str]]:
    """Return available built-in preset template choices."""
    return [
        ("blank", "Blank / Manual"),
        ("browser_kiosk_firefox", "Browser Kiosk (Firefox)"),
        ("browser_kiosk_chrome", "Browser Kiosk (Chrome)"),
        ("browser_kiosk_edge", "Browser Kiosk (Edge)"),
        ("browser_window_firefox", "Browser Window (Firefox)"),
        ("browser_window_chrome", "Browser Window (Chrome)"),
        ("browser_window_edge", "Browser Window (Edge)"),
        ("vlc_fullscreen", "VLC Fullscreen"),
        ("obs_studio", "OBS Studio"),
        ("notepad", "Notepad"),
    ]


def build_preset_template(template_id: str) -> dict[str, str]:
    """Build preset field values for a built-in template."""
    normalized = str(template_id or "").strip().lower()

    if normalized == "browser_kiosk_firefox":
        template = _build_browser_template("firefox", kiosk_mode=True)
        if template:
            template["_template_notice"] = (
                "Firefox kiosk template applied from docs/run.bat. "
                "Adjust the URL or executable path if needed."
            )
        return template

    if normalized == "browser_kiosk_chrome":
        return _build_browser_template("chrome", kiosk_mode=True)

    if normalized == "browser_kiosk_edge":
        return _build_browser_template("edge", kiosk_mode=True)

    if normalized == "browser_window_firefox":
        return _build_browser_template("firefox", kiosk_mode=False)

    if normalized == "browser_window_chrome":
        return _build_browser_template("chrome", kiosk_mode=False)

    if normalized == "browser_window_edge":
        return _build_browser_template("edge", kiosk_mode=False)

    if normalized == "vlc_fullscreen":
        executable_path = _resolve_app_path("vlc")
        working_directory = str(Path(executable_path).parent) if executable_path else ""
        return {
            "name": "VLC Fullscreen",
            "executable_path": executable_path,
            "launch_args": "--fullscreen",
            "working_directory": working_directory,
            "window_title_hint": "VLC media player",
            "_template_notice": (
                "VLC fullscreen template applied. Add a media file path to Launch Arguments if needed."
            ),
        }

    if normalized == "obs_studio":
        executable_path = _resolve_app_path("obs")
        working_directory = str(Path(executable_path).parent) if executable_path else ""
        return {
            "name": "OBS Studio",
            "executable_path": executable_path,
            "launch_args": "--disable-updater",
            "working_directory": working_directory,
            "window_title_hint": "OBS",
            "_template_notice": (
                "OBS Studio template applied. Add custom profile or scene collection arguments if needed."
            ),
        }

    if normalized == "notepad":
        executable_path = _resolve_app_path("notepad")
        working_directory = str(Path(executable_path).parent) if executable_path else ""
        return {
            "name": "Notepad",
            "executable_path": executable_path,
            "launch_args": "",
            "working_directory": working_directory,
            "window_title_hint": "Notepad",
            "_template_notice": "Notepad template applied. Useful for quick window movement tests.",
        }

    return {}
