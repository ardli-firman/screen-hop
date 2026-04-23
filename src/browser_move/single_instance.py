import win32event
import win32api
import ctypes

ERROR_ALREADY_EXISTS = 183
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


def show_already_running_message():
    """Show message box informing user app is already running."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0,
            "Browser Move Automation is already running.",
            "Already Running",
            0x30,  # MB_ICONWARNING
        )
    except Exception:
        pass
