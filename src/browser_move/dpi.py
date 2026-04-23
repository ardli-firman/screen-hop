"""DPI awareness setup for Windows."""

import ctypes
from ctypes import wintypes


def setup_dpi_awareness() -> bool:
    """Set best-available DPI awareness for the current process.

    Returns:
        True if DPI awareness was successfully set, False otherwise.
    """
    try:
        # Windows 8.1+ (Per-monitor DPI awareness)
        shcore = ctypes.windll.shcore
        set_dpi_awareness = shcore.SetProcessDpiAwareness
        set_dpi_awareness.argtypes = [ctypes.c_int]
        set_dpi_awareness.restype = ctypes.c_long
        hr = set_dpi_awareness(2)
        # S_OK (0) or E_ACCESSDENIED (already set) are both acceptable.
        return hr in (0, 0x80070005)
    except Exception:
        try:
            # Windows Vista/7 fallback (system DPI awareness)
            user32 = ctypes.windll.user32
            set_dpi_aware = user32.SetProcessDPIAware
            set_dpi_aware.restype = wintypes.BOOL
            return bool(set_dpi_aware())
        except Exception:
            return False
