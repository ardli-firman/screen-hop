# Browser Move Automation

A Windows GUI application to automatically launch browsers and move them to external monitors. Perfect for kiosks, digital signage, or multi-monitor setups.

## Features

- 🖥️ **Multi-Monitor Support**: Automatically detects and moves browsers to external monitors
- 🎨 **Modern GUI**: Built with CustomTkinter for a clean, modern interface
- 📋 **Preset Management**: Save and manage multiple browser configurations
- 🖼️ **Kiosk Mode**: Launch browsers in fullscreen kiosk mode
- 🔔 **System Tray**: Minimize to system tray for background operation
- 🔗 **Shortcuts**: Create desktop and startup shortcuts
- 🔒 **Single Instance**: Prevents multiple app instances
- ⚙️ **Configurable**: JSON-based configuration with GUI editor

## Installation (Development)

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd browser-move-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   For Windows 7 target builds, use Python `3.8.x` environment.

3. Run in development mode:
   ```bash
   python -m src.browser_move.main
   ```

## Usage

### GUI Mode

1. Launch the application
2. Create a preset with URL, browser type, and monitor
3. Click "Run Preset" to launch and move browser

### CLI Mode

Run preset directly without GUI:
```bash
python -m src.browser_move.main --preset "My Preset"
```

Run in background (tray only):
```bash
python -m src.browser_move.main --headless
```

Run preset in background:
```bash
python -m src.browser_move.main --preset "My Preset" --headless
```

## Building Executable

Build standalone executable with PyInstaller:

```bash
pyinstaller browser_move.spec
```

For Windows 7 compatibility, build with:

- Python `3.8.x`
- `pyinstaller` `<5.0` (already pinned in `requirements.txt`)

Output will be in `dist/browser_move/` directory.

## Configuration

Configuration is stored in `config.json` in the application directory:

```json
{
  "presets": [
    {
      "name": "My Preset",
      "browser_type": "firefox",
      "browser_path": "C:/Program Files/Mozilla Firefox/firefox.exe",
      "url": "https://example.com",
      "kiosk_mode": false
    }
  ],
  "theme": "System",
  "auto_start": false,
  "close_behavior": "Minimize to Tray"
}
```

### Preset Fields

- `name`: Display name for the preset
- `browser_type`: firefox, chrome, or edge
- `browser_path`: Full path to browser executable (optional, auto-detected if not set)
- `url`: URL to open in browser
- `kiosk_mode`: Launch in fullscreen kiosk mode

### Settings

- `theme`: UI theme (Dark, Light, or System)
- `auto_start`: Add to Windows startup
- `close_behavior`: Action when closing window (Exit or Minimize to Tray)

## Requirements

- Windows 7/10/11
- Python 3.8.x (recommended for build/runtime compatibility, especially Windows 7)
- Firefox, Chrome, or Edge installed

## Windows 7 Notes

- Windows 7 is end-of-life and no longer receives security updates from Microsoft.
- Build the executable on a machine with Python `3.8.x` and install Microsoft Visual C++ Redistributable if required on target machines.

## License

MIT License
