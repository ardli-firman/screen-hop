from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.browser_move import config as config_module


class ConfigNormalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._original_path = config_module.CONFIG_PATH
        self._config_path = Path(self._temp_dir.name) / "config.json"
        config_module.CONFIG_PATH = self._config_path
        config_module.consume_runtime_notices()

    def tearDown(self) -> None:
        config_module.CONFIG_PATH = self._original_path
        config_module.consume_runtime_notices()
        self._temp_dir.cleanup()

    def test_load_config_creates_default_v2_schema(self) -> None:
        loaded = config_module.load_config()

        self.assertEqual(loaded, config_module.DEFAULT_CONFIG)
        self.assertTrue(self._config_path.exists())

        saved = json.loads(self._config_path.read_text(encoding="utf-8"))
        self.assertEqual(saved, config_module.DEFAULT_CONFIG)

    def test_legacy_presets_are_cleared_and_notice_is_emitted(self) -> None:
        legacy_config = {
            "presets": [
                {
                    "name": "firefox",
                    "browser_type": "firefox",
                    "browser_path": "",
                    "url": "https://example.com",
                    "kiosk_mode": False,
                    "display_id": "display-1",
                    "display_name": "Display 1",
                }
            ],
            "theme": "Dark",
        }
        self._config_path.write_text(json.dumps(legacy_config), encoding="utf-8")

        loaded = config_module.load_config()
        notices = config_module.consume_runtime_notices()

        self.assertEqual(loaded["presets"], [])
        self.assertEqual(loaded["theme"], "Dark")
        self.assertTrue(notices)
        self.assertIn("Legacy browser presets were removed", notices[0])

        saved = json.loads(self._config_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["presets"], [])
        self.assertEqual(saved["theme"], "Dark")

    def test_universal_preset_round_trips_through_save_and_load(self) -> None:
        expected_preset = {
            "name": "OBS Studio",
            "executable_path": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
            "launch_args": "--startvirtualcam",
            "working_directory": r"C:\Program Files\obs-studio\bin\64bit",
            "window_title_hint": "OBS",
            "display_id": "display-2",
            "display_name": "Display 2",
        }
        source = {
            "presets": [expected_preset],
            "theme": "Light",
            "close_behavior": "Exit",
            "shortcut_preset": "OBS Studio",
            "startup_preset": "OBS Studio",
            "auto_start": True,
        }

        saved = config_module.save_config(source)
        loaded = config_module.load_config()

        self.assertTrue(saved)
        self.assertEqual(loaded["presets"], [expected_preset])
        self.assertEqual(loaded["theme"], "Light")
        self.assertEqual(loaded["close_behavior"], "Exit")
        self.assertEqual(loaded["shortcut_preset"], "OBS Studio")
        self.assertEqual(loaded["startup_preset"], "OBS Studio")
        self.assertTrue(loaded["auto_start"])


if __name__ == "__main__":
    unittest.main()
