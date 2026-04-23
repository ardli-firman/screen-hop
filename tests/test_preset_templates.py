from __future__ import annotations

import unittest
from unittest.mock import patch

from src.browser_move.preset_templates import (
    DEFAULT_FIREFOX_KIOSK_URL,
    build_preset_template,
    get_template_choices,
)


class PresetTemplateTests(unittest.TestCase):
    def test_template_choices_include_firefox_kiosk(self) -> None:
        choices = dict(get_template_choices())

        self.assertIn("browser_kiosk_firefox", choices)
        self.assertEqual(choices["browser_kiosk_firefox"], "Browser Kiosk (Firefox)")

    @patch("src.browser_move.preset_templates.detect_browser_path")
    def test_firefox_kiosk_template_uses_run_bat_style_arguments(
        self,
        detect_browser_path_mock,
    ) -> None:
        detect_browser_path_mock.return_value = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        template = build_preset_template("browser_kiosk_firefox")

        self.assertEqual(template["name"], "Firefox Kiosk")
        self.assertEqual(
            template["executable_path"],
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
        )
        self.assertEqual(
            template["launch_args"],
            f'--new-window --kiosk="{DEFAULT_FIREFOX_KIOSK_URL}"',
        )
        self.assertEqual(
            template["working_directory"],
            r"C:\Program Files\Mozilla Firefox",
        )
        self.assertEqual(template["window_title_hint"], "Firefox")


if __name__ == "__main__":
    unittest.main()
