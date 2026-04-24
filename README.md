# ScreenHop

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

ScreenHop is a Windows GUI app that launches one or more Windows executables and moves each new window to a chosen display. It is built with CustomTkinter, pywin32, pystray, and PyInstaller.

## Features

- Multi-program presets with per-program target display, launch arguments, working directory, and window title hint
- Browser templates for Firefox, Chrome, and Edge
- App templates for VLC, OBS, and Notepad
- System tray control for launching presets and reopening the main window
- Desktop and startup shortcuts that keep using the preset name
- Single-instance protection
- CLI support for direct preset launch

## Quick Start

```bash
pip install -r requirements.txt
python -m src.browser_move.main
```

## Presets

Each preset now contains a `programs` array. Old single-program presets are migrated automatically into the new shape.

```json
{
  "name": "Clinic Screens",
  "programs": [
    {
      "label": "Queue Browser",
      "executable_path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
      "launch_args": "--new-window https://example.com",
      "working_directory": "C:\\Program Files\\Mozilla Firefox",
      "window_title_hint": "Firefox",
      "display_id": "0:0:1920:1080:1",
      "display_name": "Display 2"
    }
  ]
}
```

In the preset editor you can add, edit, delete, and reorder programs inside a single preset. Program labels are optional, and the UI falls back to the executable filename when a label is not set.

## Usage

### GUI Mode

```bash
python -m src.browser_move.main
```

### CLI Mode

```bash
# Run a preset directly
python -m src.browser_move.main --preset "Clinic Screens"

# Start tray-only mode
python -m src.browser_move.main --headless
```

The tray menu, desktop shortcut, and startup shortcut all still launch presets by name.

## Building

```bash
pip install -r requirements.txt
pyinstaller screenhop.spec
```

Output: `dist/ScreenHop/ScreenHop.exe`

## Project Structure

- `src/browser_move/main.py` - CLI entry point and app bootstrap
- `src/browser_move/app.py` - main CustomTkinter window
- `src/browser_move/preset_form.py` - add/edit preset dialog
- `src/browser_move/preset_runner.py` - sequential multi-program execution
- `src/browser_move/config.py` - JSON config load/save and migration
- `src/browser_move/launcher.py` - executable launch helper
- `src/browser_move/monitors.py` - display detection and ID helpers
- `src/browser_move/window_mover.py` - Win32 window discovery and movement
- `src/browser_move/tray.py` - system tray menu
- `src/browser_move/settings_window.py` - settings modal
- `src/browser_move/shortcuts.py` - desktop and startup shortcut creation
- `src/browser_move/single_instance.py` - mutex-based single instance guard
- `tests/` - unit tests

## Requirements

- Windows
- Python 3.11 or newer
- CustomTkinter, pywin32, screeninfo, pystray, Pillow, winshell, and PyInstaller

## Development Notes

- Configuration lives in `config.json` at the repository root
- Use `python -m src.browser_move.main`; the package entry point is the supported dev path
- `setup_dpi_awareness()` runs first in `main()` and should stay that way
- Browser detection is path-based and should always go through `detect_browser_path()` first
- Window movement uses Win32 restore/move/verify logic with retry backoff

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a pull request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
