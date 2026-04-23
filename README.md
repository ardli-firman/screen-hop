# Browser Move Automation

Windows GUI app to launch Firefox/Chrome/Edge and move the window to a selected display.

## Features

- Multi-display detection
- Preset management
- Kiosk mode launch
- System tray support
- Desktop/startup shortcuts
- Single-instance protection

## Run In Development

```bash
pip install -r requirements.txt
python -m src.browser_move.main
```

CLI mode:

```bash
python -m src.browser_move.main --preset "My Preset"
python -m src.browser_move.main --headless
```

## Build EXE (Win7-compatible baseline)

Use a Python `3.8.x` environment when targeting Windows 7.

```bash
pip install -r requirements.txt
pyinstaller browser_move.spec
```

Output:

- `dist/browser_move/browser_move.exe`

## Build Installer (Windows 7+)

This repo includes:

- Inno Setup script: `installer/browser_move_win7.iss`
- Build helper: `build_installer.ps1`

### Prerequisites

- Python `3.8.x`
- Inno Setup 6 or 7 (`ISCC.exe`)

### One-command build (PowerShell)

```powershell
.\build_installer.ps1
```

Optional parameters:

- `-PythonCmd "C:\Path\To\python.exe"`
- `-IsccPath "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"`
- `-SkipDependencyInstall`

Installer output:

- `dist/installer/BrowserMoveAutomation-<version>-win7plus.exe`

## Windows 7 Notes

- Build with Python `3.8.x` specifically for Windows 7 target compatibility.
- Installer minimum OS is set to Windows 7 SP1 (`MinVersion=6.1sp1`).
- Installer defaults to per-user install (`{localappdata}`), so config writes do not require admin rights.

## Project Layout

```text
src/browser_move/       main package
browser_move.spec       pyinstaller build spec
installer/              inno setup script(s)
build_installer.ps1     build exe + installer
config.json             app config
```
