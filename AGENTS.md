# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-24
**Version:** 1.1.0

## OVERVIEW
Windows GUI app to launch one or more Windows executables and move each window to a selected display. Uses CustomTkinter for UI, pywin32 for window manipulation, pystray for the system tray, and PyInstaller for standalone builds.

## STRUCTURE
```
root/
|- src/browser_move/
|  |- __init__.py
|  |- __main__.py
|  |- app.py
|  |- browsers.py
|  |- config.py
|  |- dpi.py
|  |- launcher.py
|  |- main.py
|  |- monitors.py
|  |- preset_form.py
|  |- preset_runner.py
|  |- preset_templates.py
|  |- settings_window.py
|  |- shortcuts.py
|  |- single_instance.py
|  |- status_bar.py
|  |- tray.py
|  |- ui_theme.py
|  `- window_mover.py
|- tests/
|- screenhop.spec
|- config.json
|- icon.ico
|- pyproject.toml
|- setup.py
`- requirements.txt
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Entry point | `src/browser_move/main.py:main()` | CLI args: `--preset`, `--headless` |
| GUI window | `src/browser_move/app.py:MainWindow` | Preset list, details, tray callbacks |
| Program editor | `src/browser_move/preset_form.py` | Add/edit/reorder multiple programs per preset |
| Preset execution | `src/browser_move/preset_runner.py:execute_preset()` | Sequential launch/move with partial-failure summary |
| Launch executable | `src/browser_move/launcher.py:launch_executable()` | Launch any `.exe` |
| Browser helpers | `src/browser_move/browsers.py:launch_browser()` | Browser path detection + kiosk arguments |
| Find/move window | `src/browser_move/window_mover.py` | Win32 GUI automation and placement verification |
| Detect displays | `src/browser_move/monitors.py` | Display IDs, labels, and fallback resolution |
| System tray | `src/browser_move/tray.py:TrayManager` | Preset submenu, detached run |
| Config I/O | `src/browser_move/config.py` | JSON load/save and migration to `programs[]` |
| Shortcuts | `src/browser_move/shortcuts.py` | Desktop/startup `.lnk` creation |
| Settings dialog | `src/browser_move/settings_window.py` | Theme, close behavior, shortcut target |
| Single instance | `src/browser_move/single_instance.py` | Mutex-based guard |

## CONVENTIONS
- **Python 3.11+ required** - source uses modern type hints such as `dict | None`
- **Src layout** - package lives in `src/`
- **Supported dev command** - `python -m src.browser_move.main`
- **Preset schema** - presets use `name + programs[]`; each program has its own executable path, launch args, working directory, window hint, and display target
- **Program labels** - optional; UI and status text should fall back to the executable filename when label is empty
- **Execution flow** - run programs sequentially, continue after failures, and emit a final summary
- **DPI awareness** - `setup_dpi_awareness()` must run first in `main()`
- **Atomic config save** - write to `.tmp` and then `os.replace()`
- **Win32 positioning** - use restore/move/verify logic with `SWP_NOZORDER | SWP_NOACTIVATE`
- **Frozen detection** - use `getattr(sys, "frozen", False)` for exe vs dev mode

## ANTI-PATTERNS
- **DO NOT** edit `config.json` manually during app runtime - use `save_config()`
- **DO NOT** bypass the single-instance mutex
- **DO NOT** use `python.exe` for shortcuts - use `pythonw.exe`
- **DO NOT** assume a browser path exists - always call `detect_browser_path()` first
- **DO NOT** skip DPI setup on launch
- **DO NOT** reintroduce single-program assumptions in UI, tray, or preset execution code

## UNIQUE STYLES
- **Retry with exponential backoff** - `find_launched_window()` waits up to 10s and increases delay between retries
- **Thread-safe tray startup** - `icon.run_detached()` keeps Tkinter happy
- **Sequential multi-program execution** - each program is launched and moved independently
- **Frozen detection** - `getattr(sys, "frozen", False)` for exe vs dev mode

## COMMANDS
```bash
pip install -r requirements.txt
python -m src.browser_move.main
python -m src.browser_move.main --preset "My Preset"
python -m src.browser_move.main --headless
pyinstaller screenhop.spec
```

## NOTES
- **Windows-only** - pywin32 and winshell make this a Windows app
- **Config path** - `config.json` is expected in the project root
- **Built-in templates** - Firefox, Chrome, Edge, VLC, OBS, and Notepad
- **Tests** - run `python -m unittest discover -s tests`
- **Config migration** - old single-program presets are normalized into `programs[]`
