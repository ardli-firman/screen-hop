# Issues Log

## 2025-04-23 QA Verification

### Issue 1: CTkMessagebox Not Available in CustomTkinter
- **Severity**: HIGH
- **File**: `src/browser_move/preset_form.py`
- **Lines**: 306-313, 337-344
- **Description**: Code uses `ctk.CTkMessagebox` which is NOT a standard customtkinter class. This will cause AttributeError when delete confirmation or error dialogs are triggered.
- **Impact**: Application crash on preset delete or validation error
- **Root Cause**: CTkMessagebox is from a third-party package `customtkintermessagebox` which is not installed and not in requirements.txt
- **Fix Options**:
  1. Add `customtkintermessagebox` to requirements.txt
  2. Replace with standard `tkinter.messagebox.askyesno()` and `tkinter.messagebox.showerror()`

### Issue 2: PyInstaller Spec File `__file__` Undefined
- **Severity**: MEDIUM (FIXED)
- **File**: `browser_move.spec`
- **Line**: 8
- **Description**: Using `Path(__file__).parent` fails when running with `python -m PyInstaller` because `__file__` is not defined in that execution mode.
- **Fix Applied**: Changed to use `SPECPATH` variable that PyInstaller provides, with fallback options.
- **Status**: FIXED

### Issue 3: No Unit Tests
- **Severity**: LOW
- **Description**: The `tests/` directory only contains an empty `__init__.py` placeholder. No actual test files exist.
- **Impact**: No automated testing coverage
- **Recommendation**: Add unit tests for config.py, browsers.py, and other core modules