"""DPI awareness setup for Windows."""

import ctypes
from ctypes import wintypes


def setup_dpi_awareness() -> bool:
    """Set Per-Monitor DPI awareness for the current process.

    Returns:
        True if DPI awareness was successfully set, False otherwise.
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return True
    except Exception:
        return False
