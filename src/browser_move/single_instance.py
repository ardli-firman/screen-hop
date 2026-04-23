import win32event
import win32api

import ctypes

from src.browser_move import APP_NAME

ERROR_ALREADY_EXISTS = 183
# Keep the legacy mutex name so ScreenHop still blocks duplicate launches
# from older Browser Move Automation installs during upgrades.
MUTEX_NAME = "BrowserMoveAppMutex"


def check_single_instance() -> bool:
    """Check if this is the only instance running.

    Returns:
        True if this is the first instance (got the lock),
        False if another instance is already running.
    """
    try:
        # Create named mutex
        mutex = win32event.CreateMutex(None, False, MUTEX_NAME)

        # Check if mutex already existed
        if win32api.GetLastError() == ERROR_ALREADY_EXISTS:
            # Another instance is running
            win32api.CloseHandle(mutex)
            return False

        # We got the lock - don't close the handle, keep it alive
        # It will be automatically released when process exits
        return True
    except Exception:
        # If we can't create mutex, assume we're the only instance
        return True


def show_already_running_message() -> None:
    """Show message box informing user app is already running."""
    try:
        ctypes.windll.user32.MessageBoxW(
            0,
            f"{APP_NAME} is already running.",
            f"{APP_NAME} Already Running",
            0x30,  # MB_ICONWARNING
        )
    except Exception:
        pass
