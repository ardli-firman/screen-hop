"""Browser path detection for Firefox, Chrome, and Edge."""

import os
import subprocess
from pathlib import Path

# Default browser installation paths on Windows
BROWSER_PATHS = {
    "firefox": [
        "C:/Program Files/Mozilla Firefox/firefox.exe",
        "C:/Program Files (x86)/Mozilla Firefox/firefox.exe",
    ],
    "chrome": [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
    ],
    "edge": [
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    ],
}


def detect_browser_path(
    browser_type: str, custom_path: str | None = None
) -> str | None:
    """
    Detect the path to a browser executable.

    Args:
        browser_type: Browser name ('firefox', 'chrome', or 'edge')
        custom_path: Optional custom path to override detection

    Returns:
        Path to browser executable, or None if not found
    """
    # Use custom path if provided
    if custom_path:
        if os.path.exists(custom_path):
            return custom_path
        return None

    # Normalize browser type
    browser_type = browser_type.lower().strip()

    # Get default paths for browser type
    paths = BROWSER_PATHS.get(browser_type)
    if not paths:
        return None

    # Return first existing path
    for path in paths:
        if os.path.exists(path):
            return path

    return None


def launch_browser(
    browser_type: str,
    url: str,
    kiosk_mode: bool = False,
    browser_path: str | None = None,
) -> subprocess.Popen | None:
    """
    Launch a browser with optional kiosk mode.

    Args:
        browser_type: Browser name ('firefox', 'chrome', or 'edge')
        url: URL to open in the browser
        kiosk_mode: Whether to launch in kiosk mode
        browser_path: Optional custom browser path

    Returns:
        subprocess.Popen object for process tracking, or None on failure
    """
    if not browser_path:
        browser_path = detect_browser_path(browser_type)

    if not browser_path or not os.path.exists(browser_path):
        return None

    browser_type = browser_type.lower().strip()

    if browser_type == "firefox":
        if kiosk_mode:
            args = [browser_path, "--new-window", f'--kiosk="{url}"']
        else:
            args = [browser_path, "--new-window", url]
    elif browser_type == "chrome":
        if kiosk_mode:
            args = [browser_path, "--kiosk", f'--app="{url}"']
        else:
            args = [browser_path, "--new-window", url]
    elif browser_type == "edge":
        if kiosk_mode:
            args = [browser_path, "--kiosk", url]
        else:
            args = [browser_path, url]
    else:
        return None

    try:
        return subprocess.Popen(args)
    except (OSError, subprocess.SubprocessError):
        return None
