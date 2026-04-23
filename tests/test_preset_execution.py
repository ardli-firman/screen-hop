from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from src.browser_move import main as main_module
from src.browser_move import preset_runner


class PresetExecutionSmokeTests(unittest.TestCase):
    @patch.object(main_module, "show_already_running_message")
    @patch.object(main_module, "check_single_instance", return_value=False)
    @patch.object(main_module, "run_preset_direct", return_value=True)
    @patch.object(main_module, "setup_dpi_awareness")
    def test_main_allows_preset_shortcut_even_when_app_is_already_running(
        self,
        _setup_dpi_awareness,
        run_preset_direct_mock,
        check_single_instance_mock,
        show_running_message_mock,
    ) -> None:
        with patch.object(sys, "argv", ["screenhop", "--preset", "OBS Studio"]):
            exit_code = main_module.main()

        self.assertEqual(exit_code, 0)
        run_preset_direct_mock.assert_called_once_with("OBS Studio")
        check_single_instance_mock.assert_not_called()
        show_running_message_mock.assert_not_called()

    @patch.object(main_module, "execute_preset", return_value=True)
    @patch.object(
        main_module,
        "load_config",
        return_value={
            "presets": [
                {
                    "name": "OBS Studio",
                    "executable_path": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
                    "launch_args": "--startvirtualcam",
                    "working_directory": r"C:\Program Files\obs-studio\bin\64bit",
                    "window_title_hint": "OBS",
                    "display_id": "display-2",
                    "display_name": "Display 2",
                }
            ]
        },
    )
    def test_run_preset_direct_uses_universal_schema(self, _load_config, execute_preset_mock) -> None:
        success = main_module.run_preset_direct("OBS Studio")

        self.assertTrue(success)
        execute_preset_mock.assert_called_once()
        called_preset = execute_preset_mock.call_args.kwargs["reporter"]
        self.assertIs(called_preset, main_module._cli_reporter)
        self.assertEqual(execute_preset_mock.call_args.args[0]["executable_path"], r"C:\Program Files\obs-studio\bin\64bit\obs64.exe")

    @patch.object(preset_runner, "move_window_to_monitor", return_value=True)
    @patch.object(preset_runner, "find_launched_window", return_value=808)
    @patch.object(preset_runner, "launch_executable")
    @patch.object(preset_runner, "snapshot_visible_window_handles", return_value={10, 20})
    @patch.object(preset_runner, "resolve_display_for_preset")
    def test_execute_preset_reports_successful_launch_and_move(
        self,
        resolve_display_mock,
        snapshot_mock,
        launch_mock,
        find_window_mock,
        move_mock,
    ) -> None:
        class DummyProcess:
            pid = 4242

        target_display = type("Display", (), {"x": 0, "y": 0, "width": 1920, "height": 1080})()
        resolve_display_mock.return_value = (target_display, "Display 2", False)
        launch_mock.return_value = DummyProcess()

        preset = {
            "name": "OBS Studio",
            "executable_path": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
            "launch_args": "--startvirtualcam",
            "working_directory": r"C:\Program Files\obs-studio\bin\64bit",
            "window_title_hint": "OBS",
            "display_id": "display-2",
            "display_name": "Display 2",
        }
        status_updates: list[tuple[str, str]] = []

        success = preset_runner.execute_preset(
            preset,
            reporter=lambda status, message: status_updates.append((status, message)),
        )

        self.assertTrue(success)
        snapshot_mock.assert_called_once_with()
        launch_mock.assert_called_once_with(
            preset["executable_path"],
            preset["launch_args"],
            preset["working_directory"],
        )
        find_window_mock.assert_called_once_with(
            process_id=4242,
            existing_hwnds={10, 20},
            window_title_hint="OBS",
            timeout=10.0,
        )
        move_mock.assert_called_once_with(808, target_display)
        self.assertEqual(status_updates[-1][0], "ready")
        self.assertIn("moved to Display 2", status_updates[-1][1])


if __name__ == "__main__":
    unittest.main()
