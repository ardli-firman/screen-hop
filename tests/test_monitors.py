from __future__ import annotations

import unittest
from unittest.mock import patch

from src.browser_move import monitors


class DummyDisplay:
    def __init__(self, x: int, y: int, width: int, height: int, is_primary: bool, name: str) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_primary = is_primary
        self.name = name


class MonitorResolutionTests(unittest.TestCase):
    @patch("src.browser_move.monitors.get_displays")
    def test_get_display_choices_includes_primary_when_only_one_display_exists(
        self,
        get_displays_mock,
    ) -> None:
        primary = DummyDisplay(0, 0, 1920, 1080, True, r"\\.\DISPLAY1")
        get_displays_mock.return_value = [primary]

        choices = monitors.get_display_choices()

        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0][0], monitors.display_to_id(primary))
        self.assertIn("[Primary]", choices[0][1])

    @patch("src.browser_move.monitors.get_primary_display")
    @patch("src.browser_move.monitors.get_displays")
    def test_resolve_display_for_preset_falls_back_to_primary_display(
        self,
        get_displays_mock,
        get_primary_display_mock,
    ) -> None:
        primary = DummyDisplay(0, 0, 1920, 1080, True, r"\\.\DISPLAY1")
        get_displays_mock.return_value = [primary]
        get_primary_display_mock.return_value = primary

        display, label, used_fallback = monitors.resolve_display_for_preset(
            {"display_id": "missing-display"}
        )

        self.assertIs(display, primary)
        self.assertTrue(used_fallback)
        self.assertIn("[Primary]", label)


if __name__ == "__main__":
    unittest.main()
