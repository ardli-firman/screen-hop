# Window Move Automation - Learnings & Conventions

## Project Conventions

### Python Structure (src/ Layout)
- Use `src/browser_move/` as package root
- All modules importable via `from browser_move import module`
- Version in `__init__.py`

### Win32 API Patterns
- Use `EnumWindows` for finding windows (not `FindWindow`)
- Class names: Firefox=`MozillaWindowClass`, Chrome/Edge=`Chrome_WidgetWindow_`
- Must restore maximized windows before moving: `ShowWindow(hwnd, SW_RESTORE)`
- Use `SetWindowPos` for movement (not `MoveWindow`)
- Flags: `SWP_NOZORDER | SWP_NOACTIVATE` (0x0004 | 0x0010)

### Browser Launch
- Firefox kiosk: `--new-window --kiosk="url"`
- Chrome kiosk: `--kiosk --app="url"`
- Edge kiosk: `--kiosk url`
- Return `subprocess.Popen` object for tracking

### CustomTkinter Patterns
- Set theme BEFORE creating any widgets: `ctk.set_default_color_theme("blue")`
- Use `CTkComboBox` for dropdowns
- Use `CTkToplevel` with `grab_set()` for modal dialogs
- Close button protocol: `WM_DELETE_WINDOW` → minimize to tray, not exit

### System Tray (pystray)
- Use `run_detached()` for Windows (non-blocking)
- Icon size: 16x16 or 32x32
- Menu items: Show Window, Run Preset (submenu), Settings, Exit

### Config
- JSON format in project root (portable)
- Atomic writes: write to .tmp, then `os.replace()`
- Structure: presets array, theme, auto_start flag

### DPI Awareness
- Call `SetProcessDpiAwareness(2)` at startup BEFORE any window operations
- Use `ctypes.windll.shcore` on Windows 8.1+
- Fallback for older Windows versions

### Shortcuts
- Use `winshell.CreateShortcut` for desktop/startup
- Startup folder: `winshell.folder("startup")`
- Never modify registry for startup

### Single Instance Lock
- Use named mutex: `CreateMutex(None, False, "BrowserMoveAppMutex")`
- Check `GetLastError()` for `ERROR_ALREADY_EXISTS`

## Code Quality Standards
- No over-abstraction
- Minimal comments (explain "why", not "what")
- Descriptive variable names
- Handle errors gracefully
- Return meaningful values (not just None)

## Testing Notes
- Manual QA only (no automated tests)
- Evidence saved to `.sisyphus/evidence/`
- Test scenarios documented in plan
