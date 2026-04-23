from __future__ import annotations

import unittest
from unittest.mock import patch

from src.browser_move.preset_templates import (
    DEFAULT_BROWSER_URL,
    DEFAULT_FIREFOX_KIOSK_URL,
    build_preset_template,
    get_template_choices,
)


class PresetTemplateTests(unittest.TestCase):
    def test_template_choices_include_multiple_built_in_presets(self) -> None:
        choices = dict(get_template_choices())

        self.assertIn("browser_kiosk_firefox", choices)
        self.assertIn("browser_kiosk_chrome", choices)
        self.assertIn("browser_kiosk_edge", choices)
        self.assertIn("browser_window_firefox", choices)
        self.assertIn("browser_window_chrome", choices)
        self.assertIn("browser_window_edge", choices)
        self.assertIn("vlc_fullscreen", choices)
        self.assertIn("obs_studio", choices)
        self.assertIn("notepad", choices)
        self.assertEqual(choices["browser_kiosk_firefox"], "Browser Kiosk (Firefox)")
        self.assertEqual(choices["vlc_fullscreen"], "VLC Fullscreen")

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

    @patch("src.browser_move.preset_templates.detect_browser_path")
    def test_chrome_kiosk_template_uses_app_mode_arguments(
        self,
        detect_browser_path_mock,
    ) -> None:
        detect_browser_path_mock.return_value = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        template = build_preset_template("browser_kiosk_chrome")

        self.assertEqual(template["name"], "Chrome Kiosk")
        self.assertEqual(
            template["launch_args"],
            f'--kiosk --app="{DEFAULT_BROWSER_URL}"',
        )
        self.assertEqual(template["window_title_hint"], "Chrome")

    @patch("src.browser_move.preset_templates.detect_browser_path")
    def test_edge_window_template_uses_standard_url_launch(
        self,
        detect_browser_path_mock,
    ) -> None:
        detect_browser_path_mock.return_value = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

        template = build_preset_template("browser_window_edge")

        self.assertEqual(template["name"], "Edge Window")
        self.assertEqual(template["launch_args"], DEFAULT_BROWSER_URL)
        self.assertEqual(template["window_title_hint"], "Microsoft Edge")

    @patch("pathlib.Path.exists", return_value=False)
    def test_vlc_template_falls_back_to_default_path_and_fullscreen(self, _exists_mock) -> None:
        template = build_preset_template("vlc_fullscreen")

        self.assertEqual(template["name"], "VLC Fullscreen")
        self.assertEqual(template["launch_args"], "--fullscreen")
        self.assertTrue(template["executable_path"].lower().endswith("vlc.exe"))
        self.assertEqual(template["window_title_hint"], "VLC media player")

    @patch("pathlib.Path.exists", return_value=False)
    def test_obs_and_notepad_templates_are_available(self, _exists_mock) -> None:
        obs_template = build_preset_template("obs_studio")
        notepad_template = build_preset_template("notepad")

        self.assertEqual(obs_template["name"], "OBS Studio")
        self.assertEqual(obs_template["launch_args"], "--disable-updater")
        self.assertEqual(obs_template["window_title_hint"], "OBS")

        self.assertEqual(notepad_template["name"], "Notepad")
        self.assertEqual(notepad_template["launch_args"], "")
        self.assertTrue(notepad_template["executable_path"].lower().endswith("notepad.exe"))


if __name__ == "__main__":
    unittest.main()
