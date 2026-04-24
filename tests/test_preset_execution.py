from __future__ import annotations

import sys
import unittest
from unittest.mock import call, patch

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
                    "programs": [
                        {
                            "label": "OBS Main",
                            "executable_path": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
                            "launch_args": "--startvirtualcam",
                            "working_directory": r"C:\Program Files\obs-studio\bin\64bit",
                            "window_title_hint": "OBS",
                            "display_id": "display-2",
                            "display_name": "Display 2",
                        }
                    ],
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
        self.assertEqual(
            execute_preset_mock.call_args.args[0]["programs"][0]["executable_path"],
            r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        )

    @patch.object(preset_runner, "move_window_to_monitor", return_value=True)
    @patch.object(preset_runner, "find_launched_window", return_value=808)
    @patch.object(preset_runner, "launch_executable")
    @patch.object(preset_runner, "snapshot_visible_window_handles", return_value={10, 20})
    @patch.object(preset_runner, "resolve_display_for_preset")
    def test_execute_preset_runs_multiple_programs_in_order(
        self,
        resolve_display_mock,
        snapshot_mock,
        launch_mock,
        find_window_mock,
        move_mock,
    ) -> None:
        class DummyProcess:
            def __init__(self, pid: int):
                self.pid = pid

        display_one = type("Display", (), {"x": 0, "y": 0, "width": 1920, "height": 1080})()
        display_two = type("Display", (), {"x": 1920, "y": 0, "width": 1920, "height": 1080})()
        resolve_display_mock.side_effect = [
            (display_one, "Display 1", False),
            (display_two, "Display 2", False),
        ]
        launch_mock.side_effect = [DummyProcess(4242), DummyProcess(5252)]
        find_window_mock.side_effect = [808, 909]

        preset = {
            "name": "Clinic Screens",
            "programs": [
                {
                    "label": "OBS Main",
                    "executable_path": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
                    "launch_args": "--startvirtualcam",
                    "working_directory": r"C:\Program Files\obs-studio\bin\64bit",
                    "window_title_hint": "OBS",
                    "display_id": "display-1",
                    "display_name": "Display 1",
                },
                {
                    "label": "Queue Browser",
                    "executable_path": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    "launch_args": "--new-window https://example.com",
                    "working_directory": r"C:\Program Files\Mozilla Firefox",
                    "window_title_hint": "Firefox",
                    "display_id": "display-2",
                    "display_name": "Display 2",
                },
            ],
        }
        status_updates: list[tuple[str, str]] = []

        success = preset_runner.execute_preset(
            preset,
            reporter=lambda status, message: status_updates.append((status, message)),
        )

        self.assertTrue(success)
        self.assertEqual(snapshot_mock.call_count, 2)
        launch_mock.assert_has_calls(
            [
                call(
                    preset["programs"][0]["executable_path"],
                    preset["programs"][0]["launch_args"],
                    preset["programs"][0]["working_directory"],
                ),
                call(
                    preset["programs"][1]["executable_path"],
                    preset["programs"][1]["launch_args"],
                    preset["programs"][1]["working_directory"],
                ),
            ]
        )
        find_window_mock.assert_has_calls(
            [
                call(
                    process_id=4242,
                    existing_hwnds={10, 20},
                    window_title_hint="OBS",
                    timeout=10.0,
                ),
                call(
                    process_id=5252,
                    existing_hwnds={10, 20},
                    window_title_hint="Firefox",
                    timeout=10.0,
                ),
            ]
        )
        move_mock.assert_has_calls([call(808, display_one), call(909, display_two)])
        self.assertEqual(status_updates[-1][0], "ready")
        self.assertIn("all 2 programs", status_updates[-1][1])

    @patch.object(preset_runner, "move_window_to_monitor", return_value=True)
    @patch.object(preset_runner, "find_launched_window", return_value=909)
    @patch.object(preset_runner, "launch_executable")
    @patch.object(preset_runner, "snapshot_visible_window_handles", return_value={10, 20})
    @patch.object(preset_runner, "resolve_display_for_preset")
    def test_execute_preset_continues_after_program_failure(
        self,
        resolve_display_mock,
        snapshot_mock,
        launch_mock,
        find_window_mock,
        move_mock,
    ) -> None:
        class DummyProcess:
            pid = 5252

        display_one = type("Display", (), {"x": 0, "y": 0, "width": 1920, "height": 1080})()
        display_two = type("Display", (), {"x": 1920, "y": 0, "width": 1920, "height": 1080})()
        resolve_display_mock.side_effect = [
            (display_one, "Display 1", False),
            (display_two, "Display 2", False),
        ]
        launch_mock.side_effect = [None, DummyProcess()]
        preset = {
            "name": "Clinic Screens",
            "programs": [
                {
                    "label": "Broken",
                    "executable_path": r"C:\Missing\missing.exe",
                    "display_id": "display-1",
                    "display_name": "Display 1",
                },
                {
                    "label": "Queue Browser",
                    "executable_path": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    "display_id": "display-2",
                    "display_name": "Display 2",
                },
            ],
        }
        status_updates: list[tuple[str, str]] = []

        success = preset_runner.execute_preset(
            preset,
            reporter=lambda status, message: status_updates.append((status, message)),
        )

        self.assertFalse(success)
        self.assertEqual(snapshot_mock.call_count, 2)
        self.assertEqual(launch_mock.call_count, 2)
        find_window_mock.assert_called_once()
        move_mock.assert_called_once_with(909, display_two)
        self.assertEqual(status_updates[-1][0], "error")
        self.assertIn("1/2 programs", status_updates[-1][1])

    @patch.object(preset_runner, "move_window_to_monitor")
    @patch.object(preset_runner, "find_launched_window")
    @patch.object(preset_runner, "launch_executable", return_value=None)
    @patch.object(preset_runner, "snapshot_visible_window_handles", return_value=set())
    @patch.object(preset_runner, "resolve_display_for_preset")
    def test_execute_preset_reports_all_failed(
        self,
        resolve_display_mock,
        _snapshot_mock,
        _launch_mock,
        find_window_mock,
        move_mock,
    ) -> None:
        display = type("Display", (), {"x": 0, "y": 0, "width": 1920, "height": 1080})()
        resolve_display_mock.return_value = (display, "Display 1", False)
        preset = {
            "name": "Broken Screens",
            "programs": [
                {
                    "label": "One",
                    "executable_path": r"C:\Missing\one.exe",
                    "display_id": "display-1",
                    "display_name": "Display 1",
                },
                {
                    "label": "Two",
                    "executable_path": r"C:\Missing\two.exe",
                    "display_id": "display-1",
                    "display_name": "Display 1",
                },
            ],
        }
        status_updates: list[tuple[str, str]] = []

        success = preset_runner.execute_preset(
            preset,
            reporter=lambda status, message: status_updates.append((status, message)),
        )

        self.assertFalse(success)
        find_window_mock.assert_not_called()
        move_mock.assert_not_called()
        self.assertEqual(status_updates[-1][0], "error")
        self.assertIn("0/2 programs", status_updates[-1][1])


if __name__ == "__main__":
    unittest.main()
