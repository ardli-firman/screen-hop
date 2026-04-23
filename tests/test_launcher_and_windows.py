from __future__ import annotations

import unittest

from src.browser_move.launcher import build_command_line
from src.browser_move.window_mover import WindowCandidate, choose_window_candidate


class LauncherAndWindowSelectionTests(unittest.TestCase):
    def test_build_command_line_preserves_windows_arguments(self) -> None:
        command_line = build_command_line(
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            '--fullscreen --meta-title "Lobby Display"',
        )

        self.assertTrue(command_line.startswith('"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"'))
        self.assertIn('--fullscreen --meta-title "Lobby Display"', command_line)

    def test_choose_window_candidate_prefers_process_id(self) -> None:
        candidates = [
            WindowCandidate(hwnd=100, title="Helper", class_name="App", area=80_000, pid=11),
            WindowCandidate(hwnd=200, title="Main Window", class_name="App", area=320_000, pid=42),
            WindowCandidate(hwnd=300, title="Other", class_name="App", area=450_000, pid=77),
        ]

        selected = choose_window_candidate(candidates, process_id=42, window_title_hint="Other")

        self.assertIsNotNone(selected)
        self.assertEqual(selected.hwnd, 200)

    def test_choose_window_candidate_uses_title_hint_when_pid_does_not_match(self) -> None:
        candidates = [
            WindowCandidate(hwnd=100, title="Control Room", class_name="App", area=180_000, pid=11),
            WindowCandidate(hwnd=200, title="Lobby Dashboard", class_name="App", area=160_000, pid=12),
            WindowCandidate(hwnd=300, title="Untitled", class_name="App", area=420_000, pid=13),
        ]

        selected = choose_window_candidate(candidates, process_id=999, window_title_hint="dashboard")

        self.assertIsNotNone(selected)
        self.assertEqual(selected.hwnd, 200)

    def test_choose_window_candidate_falls_back_to_largest_new_window(self) -> None:
        candidates = [
            WindowCandidate(hwnd=100, title="Tiny", class_name="App", area=80_000, pid=11),
            WindowCandidate(hwnd=200, title="", class_name="Splash", area=540_000, pid=12),
            WindowCandidate(hwnd=300, title="Medium", class_name="App", area=220_000, pid=13),
        ]

        selected = choose_window_candidate(candidates)

        self.assertIsNotNone(selected)
        self.assertEqual(selected.hwnd, 200)


if __name__ == "__main__":
    unittest.main()
