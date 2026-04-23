# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-23
**Version:** 1.0.0

## OVERVIEW
Windows GUI app to launch browsers and move them to external monitors. Uses CustomTkinter for UI, pywin32 for window manipulation, pystray for system tray. Built as standalone exe via PyInstaller.

## STRUCTURE
```
root/
├── src/browser_move/    # Main package (14 modules)
│   ├── main.py          # Entry point + CLI args
│   ├── app.py           # MainWindow GUI class
│   ├── browsers.py      # Browser path detection + launch
│   ├── config.py        # JSON config load/save
│   ├── window_mover.py  # Win32 window find + move
│   ├── monitors.py      # screeninfo wrapper
│   ├── tray.py          # pystray system tray
│   ├── shortcuts.py     # Desktop/startup .lnk creation
│   ├── settings_window.py # Settings modal dialog
│   ├── preset_form.py   # Add/edit preset form
│   ├── single_instance.py # Mutex-based single instance
│   ├── dpi.py           # DPI awareness setup
│   └── status_bar.py    # Status bar component
├── tests/               # Test stub (empty - needs tests)
├── docs/                # Misc files (exe, ps1, bat)
├── browser_move.spec    # PyInstaller build config
├── config.json          # App config (presets, theme, settings)
├── icon.ico             # Application icon
├── pyproject.toml       # Build config (CLI entry misconfigured)
├── setup.py             # Minimal setuptools stub
└── requirements.txt     # Dependencies
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Entry point | `src/browser_move/main.py:main()` | CLI args: --preset, --headless |
| GUI window | `src/browser_move/app.py:MainWindow` | CustomTkinter, preset management |
| Launch browser | `src/browser_move/browsers.py:launch_browser()` | Firefox/Chrome/Edge, kiosk mode |
| Find/move window | `src/browser_move/window_mover.py` | win32gui, class name matching |
| Detect monitors | `src/browser_move/monitors.py` | screeninfo, external filter |
| System tray | `src/browser_move/tray.py:TrayManager` | pystray, preset submenu |
| Config I/O | `src/browser_move/config.py` | JSON atomic save |
| Shortcuts | `src/browser_move/shortcuts.py` | winshell, win32com.client |
| Settings dialog | `src/browser_move/settings_window.py` | Theme, auto-start, close behavior |
| Add/edit preset | `src/browser_move/preset_form.py` | Modal form, validation |
| Single instance | `src/browser_move/single_instance.py` | Named mutex |

## CONVENTIONS
- **Python 3.11+ required** - uses modern type hints (`dict | None` syntax)
- **Src layout** - package in `src/`, not root
- **CLI entry misconfigured** - pyproject.toml references `__main__` which doesn't exist; use `python -m src.browser_move.main`
- **CustomTkinter theme** - `ctk.set_appearance_mode("System")`, blue theme
- **DPI awareness** - `setup_dpi_awareness()` called first in main()
- **Atomic config save** - writes to `.tmp` then `os.replace()`
- **Window class names** - Firefox: `MozillaWindowClass`, Chrome/Edge: `Chrome_WidgetWin_`

## ANTI-PATTERNS (THIS PROJECT)
- **DO NOT** edit config.json manually during app runtime - use `save_config()`
- **DO NOT** bypass single-instance check - mutex prevents duplicate tray icons
- **DO NOT** use `python.exe` for shortcuts - use `pythonw.exe` (no console)
- **DO NOT** assume browser path exists - always call `detect_browser_path()` first
- **DO NOT** skip DPI setup on launch - critical for correct window positioning

## UNIQUE STYLES
- **Retry with exponential backoff** - `find_browser_window()` waits up to 10s, doubles delay each retry
- **Thread-safe tray menu** - `icon.run_detached()` for Tkinter compatibility
- **Win32 window positioning** - `SWP_NOZORDER | SWP_NOACTIVATE` flags, restore before move
- **Frozen detection** - `getattr(sys, "frozen", False)` for exe vs dev mode

## COMMANDS
```bash
# Development
pip install -r requirements.txt
python -m src.browser_move.main               # GUI mode
python -m src.browser_move.main --preset "My Preset"  # CLI run preset
python -m src.browser_move.main --headless    # Tray only

# Build executable
pyinstaller browser_move.spec                 # Output: dist/browser_move/
```

## NOTES
- **Windows-only** - pywin32, winshell dependencies; no cross-platform support
- **Config path** - `config.json` expected in project root (3 levels up from config.py)
- **Browser detection** - hardcoded Windows paths in `BROWSER_PATHS` dict
- **Empty tests** - `tests/__init__.py` only; no test coverage
- **docs/ contents** - contains exe/bat/ps1 files (unusual for docs directory)
- **Kiosk mode args differ** - Firefox: `--kiosk="url"`, Chrome: `--kiosk --app="url"`, Edge: `--kiosk url`