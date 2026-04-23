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
