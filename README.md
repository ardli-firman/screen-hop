# ScreenHop

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.11-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

A Windows GUI application to automatically launch browsers (Firefox, Chrome, Edge) and move them to selected external displays. Perfect for multi-monitor setups, digital signage, and kiosk deployments.

## Features

- **Multi-display Detection** - Automatically detects all connected monitors
- **Preset Management** - Save and reuse browser launch configurations
- **Kiosk Mode Launch** - Launch browsers in full-screen kiosk mode
- **System Tray Support** - Minimal UI with background operation
- **Desktop & Startup Shortcuts** - Easy access and auto-start capabilities
- **Single-instance Protection** - Prevents duplicate app instances
- **CLI Support** - Run presets directly from command line
- **Windows 7+ Compatible** - Works on Windows 7 SP1 and later

## Screenshots

*Coming soon*

## Installation

### Pre-built Installer (Recommended)

Download the latest installer from the [Releases](https://github.com/ardli-firman/screen-hop/releases) page.

The installer:
- Requires no admin rights (per-user installation)
- Creates desktop shortcuts automatically
- Supports Windows 7 SP1 and later

### Manual Installation

```bash
pip install -r requirements.txt
python -m src.browser_move.main
```

## Usage

### GUI Mode

Launch the application to access the main window:

```bash
python -m src.browser_move.main
```

Create presets by selecting:
1. Browser type (Firefox, Chrome, Edge)
2. Target URL
3. Destination monitor
4. Window size (optional)

### CLI Mode

Run presets directly without opening the GUI:

```bash
# Run a specific preset
python -m src.browser_move.main --preset "My Preset"

# Run in headless mode (system tray only)
python -m src.browser_move.main --headless
```

### System Tray

When running, ScreenHop appears in the system tray with:
- Quick preset launch menu
- Settings access
- Show/hide main window

## Building

### Build Executable

```bash
pip install -r requirements.txt
pyinstaller screenhop.spec
```

Output: `dist/ScreenHop/ScreenHop.exe`

### Build Installer (Windows 7+)

Prerequisites:
- Python 3.8.x (for Windows 7 compatibility)
- Inno Setup 6 or 7

One-command build (PowerShell):

```powershell
.\build_installer.ps1
```

Optional parameters:
```powershell
.\build_installer.ps1 -PythonCmd "C:\Path\To\python.exe" -IsccPath "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Output: `dist/installer/ScreenHop-<version>-win7plus.exe`

### Windows 7 Compatibility Notes

- Build with Python 3.8.x for Windows 7 target
- Installer minimum OS: Windows 7 SP1 (`MinVersion=6.1sp1`)
- Per-user installation (`{localappdata}`) avoids admin requirement

## Project Structure

```
screenhop/
├── src/browser_move/       # Main application package
│   ├── main.py             # Entry point + CLI
│   ├── app.py              # Main GUI window
│   ├── browsers.py         # Browser detection & launch
│   ├── window_mover.py     # Win32 window positioning
│   ├── monitors.py         # Multi-display detection
│   ├── tray.py             # System tray management
│   ├── config.py           # Configuration I/O
│   └── presets.py          # Preset management
├── installer/              # Inno Setup scripts
├── tests/                  # Test suite
├── screenhop.spec          # PyInstaller config
├── build_installer.ps1     # Build automation
├── config.json             # Application config
└── requirements.txt        # Dependencies
```

## Requirements

- Python 3.8+ (3.11+ recommended)
- Windows 7 SP1 or later
- Supported browsers: Firefox, Chrome, Edge

Dependencies:
- CustomTkinter - Modern Tkinter UI
- pywin32 - Windows API integration
- screeninfo - Monitor detection
- pystray - System tray support
- pyinstaller - Executable building

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ardli-firman/screenhop.git
cd screenhop

# Install dependencies
pip install -r requirements.txt

# Run in development
python -m src.browser_move.main
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Keep functions focused and modular

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern UI components
- [pywin32](https://github.com/mhammond/pywin32) for Windows API access
- [screeninfo](https://github.com/rr-/screeninfo) for monitor detection

## Support

- **Issues**: [GitHub Issues](https://github.com/ardli-firman/screen-hop/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ardli-firman/screen-hop/discussions)

---

Made with ❤️ for multi-monitor users