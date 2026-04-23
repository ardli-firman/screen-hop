"""JSON config manager for ScreenHop."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Config path: 3 levels up from src/browser_move/config.py -> project root
CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "presets": [],
    "theme": "System",
    "auto_start": False,
    "close_behavior": "Minimize to Tray",
    "shortcut_preset": "",
    "startup_preset": "",
}

PRESET_KEYS = (
    "name",
    "executable_path",
    "launch_args",
    "working_directory",
    "window_title_hint",
    "display_id",
    "display_name",
)
LEGACY_PRESET_FIELDS = {"browser_type", "browser_path", "url", "kiosk_mode"}
VALID_THEMES = {"Dark", "Light", "System"}
VALID_CLOSE_BEHAVIORS = {"Exit", "Minimize to Tray"}
_RUNTIME_NOTICES: list[str] = []


def _queue_runtime_notice(message: str) -> None:
    if message not in _RUNTIME_NOTICES:
        _RUNTIME_NOTICES.append(message)


def consume_runtime_notices() -> list[str]:
    """Return and clear runtime notices collected during config normalization."""
    notices = list(_RUNTIME_NOTICES)
    _RUNTIME_NOTICES.clear()
    return notices


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in {"true", "True", "1", 1}:
        return True
    if value in {"false", "False", "0", 0}:
        return False
    return default


def _is_legacy_preset(preset: dict[str, Any]) -> bool:
    return bool(LEGACY_PRESET_FIELDS.intersection(preset.keys())) or "executable_path" not in preset


def _normalize_preset(preset: dict[str, Any]) -> dict[str, str] | None:
    name = _normalize_text(preset.get("name"))
    executable_path = _normalize_text(preset.get("executable_path"))
    display_id = _normalize_text(preset.get("display_id") or preset.get("monitor_id"))
    display_name = _normalize_text(preset.get("display_name") or preset.get("monitor_name"))

    if not name or not executable_path or not display_id:
        return None

    return {
        "name": name,
        "executable_path": executable_path,
        "launch_args": _normalize_text(preset.get("launch_args")),
        "working_directory": _normalize_text(preset.get("working_directory")),
        "window_title_hint": _normalize_text(preset.get("window_title_hint")),
        "display_id": display_id,
        "display_name": display_name or display_id,
    }


def _normalize_config(raw_data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    normalized = DEFAULT_CONFIG.copy()
    mutated = False

    theme = _normalize_text(raw_data.get("theme")) or DEFAULT_CONFIG["theme"]
    if theme not in VALID_THEMES:
        theme = DEFAULT_CONFIG["theme"]
        mutated = True
    normalized["theme"] = theme

    close_behavior = (
        _normalize_text(raw_data.get("close_behavior")) or DEFAULT_CONFIG["close_behavior"]
    )
    if close_behavior not in VALID_CLOSE_BEHAVIORS:
        close_behavior = DEFAULT_CONFIG["close_behavior"]
        mutated = True
    normalized["close_behavior"] = close_behavior

    normalized["auto_start"] = _normalize_bool(
        raw_data.get("auto_start"), DEFAULT_CONFIG["auto_start"]
    )
    normalized["shortcut_preset"] = _normalize_text(raw_data.get("shortcut_preset"))
    normalized["startup_preset"] = _normalize_text(raw_data.get("startup_preset"))

    raw_presets = raw_data.get("presets", [])
    if not isinstance(raw_presets, list):
        mutated = True
        raw_presets = []

    normalized_presets: list[dict[str, str]] = []
    legacy_detected = False

    for preset in raw_presets:
        if not isinstance(preset, dict):
            mutated = True
            continue

        if _is_legacy_preset(preset):
            legacy_detected = True
            break

        normalized_preset = _normalize_preset(preset)
        if normalized_preset is None:
            mutated = True
            continue
        normalized_presets.append(normalized_preset)

    if legacy_detected:
        normalized["presets"] = []
        mutated = True
        _queue_runtime_notice(
            "Legacy browser presets were removed. Create a new app preset for ScreenHop V2."
        )
    else:
        normalized["presets"] = normalized_presets

    valid_preset_names = {preset["name"] for preset in normalized["presets"]}
    shortcut_preset = normalized["shortcut_preset"]
    startup_preset = normalized["startup_preset"]

    if shortcut_preset and shortcut_preset not in valid_preset_names:
        normalized["shortcut_preset"] = ""
        mutated = True
    if startup_preset and startup_preset not in valid_preset_names:
        normalized["startup_preset"] = ""
        normalized["auto_start"] = False
        mutated = True

    return normalized, mutated


def _serializable_config(data: dict[str, Any]) -> dict[str, Any]:
    config, _ = _normalize_config(data)
    config["presets"] = [
        {key: preset.get(key, "") for key in PRESET_KEYS}
        for preset in config.get("presets", [])
        if isinstance(preset, dict)
    ]
    return config


def load_config() -> dict[str, Any]:
    """Load config from JSON file and normalize it."""
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)

        if not isinstance(data, dict):
            raise ValueError("Config root must be an object")

        config, mutated = _normalize_config(data)
        if mutated:
            save_config(config)
        return config

    except json.JSONDecodeError as exc:
        print(f"[config] Invalid JSON in config file: {exc}, using default config")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    except Exception as exc:
        print(f"[config] Error loading config: {exc}, using default config")
        return DEFAULT_CONFIG.copy()


def save_config(data: dict[str, Any]) -> bool:
    """Save config to JSON file atomically."""
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp_path = CONFIG_PATH.with_suffix(".tmp")
        serializable = _serializable_config(data)

        with open(temp_path, "w", encoding="utf-8") as file_obj:
            json.dump(serializable, file_obj, indent=2)

        os.replace(temp_path, CONFIG_PATH)
        return True

    except Exception as exc:
        print(f"[config] Error saving config: {exc}")
        try:
            temp_path = CONFIG_PATH.with_suffix(".tmp")
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass
        return False
