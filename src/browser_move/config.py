"""JSON config manager for browser_move."""

import json
import os
from pathlib import Path
from typing import Any, Dict

# Config path: 3 levels up from src/browser_move/config.py -> project root
CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {"presets": [], "theme": "System", "auto_start": False}


def load_config() -> Dict[str, Any]:
    """Load config from JSON file.

    Returns:
        Dict with config data. Creates default config if file missing or invalid.
    """
    if not CONFIG_PATH.exists():
        print(f"[config] Config not found at {CONFIG_PATH}, creating default config")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ensure all required keys exist
        config = DEFAULT_CONFIG.copy()
        config.update(data)

        # Validate presets structure
        for preset in config.get("presets", []):
            if not isinstance(preset, dict):
                config["presets"] = []
                break
            # Ensure each preset has required fields
            required_fields = [
                "name",
                "browser_type",
                "browser_path",
                "url",
                "kiosk_mode",
            ]
            if not all(field in preset for field in required_fields):
                config["presets"] = []
                print("[config] Preset missing required fields, resetting presets")
                break

        return config

    except json.JSONDecodeError as e:
        print(f"[config] Invalid JSON in config file: {e}, using default config")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"[config] Error loading config: {e}, using default config")
        return DEFAULT_CONFIG.copy()


def save_config(data: Dict[str, Any]) -> bool:
    """Save config to JSON file atomically.

    Args:
        data: Config dictionary to save.

    Returns:
        True if save succeeded, False otherwise.
    """
    try:
        # Ensure parent directory exists
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file first, then atomic replace
        temp_path = CONFIG_PATH.with_suffix(".tmp")

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Atomic replace (works on Windows)
        os.replace(temp_path, CONFIG_PATH)

        return True

    except Exception as e:
        print(f"[config] Error saving config: {e}")
        # Clean up temp file if it exists
        try:
            temp_path = CONFIG_PATH.with_suffix(".tmp")
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass
        return False
