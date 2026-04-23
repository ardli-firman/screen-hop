# Window Move Automation - Work Plan

## TL;DR

> **Quick Summary**: Build a Python GUI application (CustomTkinter) that manages browser display on external monitors with multiple presets, system tray integration, Windows startup/shortcuts, and PyInstaller exe packaging using modern src/ layout structure.
> 
> **Deliverables**:
> - Desktop GUI application with preset management (src/browser_move/ modules)
> - Browser launcher (Firefox, Chrome, Edge) with optional kiosk mode
> - Window mover to external monitor with maximize
> - System tray integration with quick access menu
> - Desktop shortcut and Windows startup integration
> - Portable JSON config in app folder
> - PyInstaller exe build capability (--onedir mode)
> - Modern Python packaging (pyproject.toml)
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Project Structure → Config → Monitor Detection → Browser Launcher → Window Mover → GUI → Integration → Build Config → Final Verification

---

## Context

### Original Request
User wants to create a Python project to automatically move browser/program to external monitor based on shortcuts during Windows startup or desktop shortcuts. Currently has manual solution in `docs\run.bat` using monitor.exe, run.exe, and PowerShell. Goal: simplify configuration with GUI for settings (program location, URL, monitor selection).

### Interview Summary
**Key Discussions**:
- Config format: GUI Windows App with form editing (not file-based config)
- Execution method: GUI Window App (not CLI)
- Monitor selection: Non-primary monitor auto-detection
- Tools strategy: Python native libraries (pywin32, screeninfo) - no external exe dependencies
- Presets: Multiple presets support (antrian poli, apotek, etc)
- Browser support: Firefox, Chrome, Edge
- Startup integration: Startup folder shortcut
- Additional features: System tray, auto-start toggle, desktop shortcut creation
- Kiosk mode: Optional (toggle in GUI)
- Window position: Maximize after move
- Config location: Portable (same folder)
- UI framework: CustomTkinter for modern look
- Test strategy: No automated tests, agent QA scenarios
- Build exe: YES - Directory Mode (--onedir) with PyInstaller
- Project structure: src/ Layout - Modern Python packaging with pyproject.toml

**Research Findings**:
- Window manipulation: Use `EnumWindows` + title matching, `SetWindowPos` for movement
- Must restore maximized windows before moving
- DPI awareness must be set before enumeration
- Browser class names: Firefox=`MozillaWindowClass`, Chrome/Edge=`Chrome_WidgetWindow_`
- System tray: Use `pystray` with `run_detached()` for Tkinter integration
- Shortcuts: Use `winshell.CreateShortcut` for desktop/startup
- CustomTkinter: Theme must be set BEFORE creating widgets
- PyInstaller: Use --onedir for smaller exe size, --windowed for GUI apps
- src/ layout: Standard modern Python packaging pattern

### Metis Review
**Identified Gaps** (addressed):
- Multiple external monitors: Show selection dialog if more than 1 external detected (default applied)
- Close button behavior: Minimize to tray, not exit (default applied)
- No external monitor: Show error dialog, don't exit app (default applied)
- Preset auto-run: Manual trigger only, no auto-run on app start (default applied)
- Browser already running: Open new window instance (default applied)
- Single instance lock: Use named mutex to prevent duplicate instances (added as requirement)
- DPI awareness: Set before any window operations (technical requirement)

---

## Work Objectives

### Core Objective
Create a portable Python GUI application that enables users to:
1. Manage multiple browser display presets (URL, browser type, kiosk mode)
2. Launch browser and automatically move to external monitor
3. Integrate with Windows system tray and startup/desktop shortcuts
4. Build to standalone exe using PyInstaller

### Concrete Deliverables (Senior Dev Structure)
```
src/browser_move/
├── __init__.py              # Package init with version
├── main.py                  # Entry point with DPI setup
├── app.py                   # Main CustomTkinter window
├── config.py                # JSON config manager
├── monitors.py              # Monitor detection (screeninfo)
├── browsers.py              # Browser path/launch/window finding
├── window_mover.py          # Window movement (pywin32)
├── tray.py                  # System tray (pystray)
├── shortcuts.py             # Desktop/Startup shortcuts (winshell)
├── settings_window.py       # Settings CTkToplevel
├── preset_form.py           # Preset management UI
├── status_bar.py            # Status display component
├── dpi.py                   # DPI awareness setup
└── single_instance.py       # Single instance lock

Project Root:
├── pyproject.toml           # Modern Python packaging config
├── setup.py                 # Legacy setup.py for pip install
├── browser_move.spec        # PyInstaller spec file (--onedir)
├── requirements.txt         # Dependencies list
├── config.json              # Runtime configuration
├── icon.ico                 # Application icon
├── README.md                # Project documentation
├── .gitignore               # Git ignore patterns
└── tests/__init__.py        # Test placeholder
```

### Definition of Done
- [ ] Application launches with GUI showing preset list
- [ ] Preset can be added/edited/deleted through GUI
- [ ] Browser launches and moves to external monitor correctly
- [ ] System tray icon appears when app runs
- [ ] Desktop shortcut created via GUI button
- [ ] Startup folder shortcut toggle works
- [ ] Single instance lock prevents duplicate instances
- [ ] Error handling for no external monitor and browser not found
- [ ] Project can be built to exe with `pyinstaller browser_move.spec`
- [ ] Exe runs standalone without Python installed

### Must Have
- src/ layout structure (src/browser_move/)
- pyproject.toml for modern packaging
- PyInstaller spec file for exe build (--onedir mode)
- GUI with preset management (add/edit/delete)
- Browser launcher (Firefox, Chrome, Edge)
- Window mover to non-primary monitor
- System tray integration
- Desktop shortcut creation button
- Startup folder shortcut toggle
- JSON config persistence
- Single instance lock
- DPI awareness setup
- .gitignore file

### Must NOT Have (Guardrails)
- External exe dependencies (monitor.exe, run.exe, nircmd) - use Python native only
- Registry modification for startup - use startup folder only
- Flat project structure - use src/ layout
- Auto-run preset on app start (manual trigger only)
- Hotkey support (not requested by user)
- Logging feature (user confirmed no tests/troubleshooting needed)
- AI-slop patterns: over-abstraction, excessive comments, generic names

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (new project)
- **Automated tests**: None
- **Framework**: None
- **Agent-Executed QA**: YES - Manual QA automation via interactive testing

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **GUI Testing**: Use Playwright for visual verification, screenshots
- **Window/Monitor Testing**: Use Python REPL to verify monitor detection, window finding
- **Shortcut Testing**: Use PowerShell to verify shortcut file existence
- **Config Testing**: Use Bash to verify JSON file content
- **Build Testing**: Use PyInstaller to build exe, verify exe runs

---

## Execution Strategy

### Parallel Execution Waves (CORRECTED - Respects Dependencies)

> Waves are structured to respect actual task dependencies. Sequential dependencies are handled by splitting into sub-waves or marking tasks as sequential.

```
Wave 0 (Start First - MUST complete before all others):
└── Task 1: Project structure setup (src/, pyproject.toml, .gitignore) [quick]
    → Sequential - creates src/browser_move/ directory required by all subsequent tasks

Wave 1 (After Wave 0 - foundation modules, TRUE parallel):
├── Task 2: Requirements.txt + dependencies [quick]
├── Task 3: Config manager module [quick]
├── Task 4: Monitor detection module [quick]
├── Task 5: Browser path detection module [quick]
├── Task 6: Icon file setup [quick]
└── Task 10: DPI awareness setup [quick]
    → All can run in parallel after Task 1 creates src/ structure

Wave 2 (After Wave 1 - browser functionality, SEQUENTIAL):
├── Task 7: Browser launcher module [unspecified-high]
│   → Depends on Task 5 (browser path detection)
├── Task 8: Window finder module [unspecified-high]
│   → Depends on Task 7 (needs browser launched to find window)
└── Task 9: Window mover module [unspecified-high]
    → Depends on Task 4 (monitor) + Task 8 (window hwnd)
    → NOTE: Tasks 7 → 8 → 9 are sequential, not parallel

Wave 3 (After Wave 2 - GUI components, TRUE parallel):
├── Task 11: Main GUI window [visual-engineering]
├── Task 12: Preset form component [visual-engineering]
├── Task 13: Settings window [visual-engineering]
└── Task 14: Status bar component [visual-engineering]
    → All can run in parallel after Task 1 (structure), Task 3 (config), Task 11 needs main window for 12-14

Wave 4 (After Wave 3 - integration, PARTIAL parallel):
├── Task 15: System tray integration [unspecified-high] - needs Task 6 (icon), Task 11 (window)
├── Task 16: Shortcut creation module [unspecified-high] - needs Task 3 (config)
├── Task 17: Single instance lock [quick] - standalone, can be parallel
    → Tasks 15, 16, 17 can run in parallel

Wave 5 (After Wave 4 - entry point, SEQUENTIAL):
└── Task 18: Entry point integration [unspecified-high]
    → Depends on ALL previous tasks (1-17)
    → Sequential - integrates everything

Wave 6 (After Wave 5 - build + docs, TRUE parallel):
├── Task 19: PyInstaller spec file [quick]
└── Task 20: README documentation [writing]
    → Both can run in parallel after Task 18

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA + exe build test (unspecified-high)
├── Task F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay
```

### Dependency Matrix (CORRECTED - Aligned with Waves)

- **1**: - (no dependencies) → Wave 0 (MUST be first)
- **2**: 1 (needs src/ structure) → Wave 1
- **3**: 1 (needs src/ structure) → Wave 1
- **4**: 1 (needs src/ structure) → Wave 1
- **5**: 1 (needs src/ structure) → Wave 1
- **6**: - (standalone) → Wave 1
- **7**: 5 (needs browser path) → Wave 2 (sequential after Task 5)
- **8**: 7 (needs browser launched) → Wave 2 (sequential after Task 7)
- **9**: 4, 8 (needs monitor + hwnd) → Wave 2 (sequential after Task 8)
- **10**: - (standalone) → Wave 1 (moved up, no dependencies)
- **11**: 1, 3, 4 (needs structure, config, monitor) → Wave 3
- **12**: 3, 11 (needs config + main window) → Wave 3 (must wait for Task 11)
- **13**: 11 (needs main window) → Wave 3 (must wait for Task 11)
- **14**: 11 (needs main window) → Wave 3 (must wait for Task 11)
- **15**: 6, 11 (needs icon + main window) → Wave 4
- **16**: 3 (needs config) → Wave 4
- **17**: - (standalone) → Wave 4
- **18**: 1-17 (needs ALL modules) → Wave 5 (sequential)
- **19**: 18 (needs entry point) → Wave 6
- **20**: - (can write anytime) → Wave 6

### Agent Dispatch Summary

- **Wave 0**: 1 agent → T1 `quick` (sequential, must complete first)
- **Wave 1**: 6 agents → T2-T6, T10 all `quick` (parallel after T1)
- **Wave 2**: 3 agents → T7-T9 all `unspecified-high` (but SEQUENTIAL execution)
- **Wave 3**: 4 agents → T11 first, then T12-T14 `visual-engineering` (T11 must complete first)
- **Wave 4**: 3 agents → T15-T16 `unspecified-high`, T17 `quick` (parallel)
- **Wave 5**: 1 agent → T18 `unspecified-high` (sequential, integrates all)
- **Wave 6**: 2 agents → T19 `quick`, T20 `writing` (parallel)
- **Wave FINAL**: 4 agents → F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. Project Structure Setup (src/ Layout)

  **What to do**:
  - Create `src/browser_move/` directory structure
  - Create `pyproject.toml` with modern Python packaging config
  - Create `setup.py` for legacy pip install support
  - Create `.gitignore` for Python project (exclude __pycache__, .pyc, dist/, build/)
  - Create `tests/__init__.py` placeholder
  - Create empty `src/browser_move/__init__.py` with version string

  **Must NOT do**:
  - Don't use flat structure (must use src/ layout)
  - Don't create complex build scripts

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple directory and config file creation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 0 (SEQUENTIAL - must complete first)
  - **Blocks**: ALL subsequent tasks (2-20)
  - **Blocked By**: None

  **References**:
  - Modern Python packaging: pyproject.toml with [build-system], [project] sections
  - src/ layout: src/package_name/ is standard pattern

  **Acceptance Criteria**:
  - [ ] `src/browser_move/` directory exists
  - [ ] `pyproject.toml` exists with valid config
  - [ ] `setup.py` exists
  - [ ] `.gitignore` exists with Python patterns
  - [ ] `tests/__init__.py` exists

  **QA Scenarios**:
  ```
  Scenario: Verify project structure
    Tool: Bash
    Steps:
      1. ls -la src/browser_move/
      2. ls pyproject.toml setup.py .gitignore tests/
    Expected Result: All files and directories exist
    Evidence: .sisyphus/evidence/task-01-structure.txt

  Scenario: Verify pyproject.toml valid
    Tool: Bash (Python)
    Steps:
      1. python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
    Expected Result: No error, valid TOML
    Evidence: .sisyphus/evidence/task-01-toml.txt
  ```

  **Commit**: YES
  - Message: `feat: initialize project with src/ layout and pyproject.toml`
  - Files: src/browser_move/__init__.py, pyproject.toml, setup.py, .gitignore, tests/__init__.py

- [x] 2. Requirements.txt + Dependencies

  **What to do**:
  - Create `requirements.txt` with all dependencies
  - Dependencies: customtkinter, pywin32, screeninfo, pystray, Pillow, winshell, pyinstaller
  - Create empty `config.json` with initial structure in project root
  - Add dev dependencies section if needed

  **Must NOT do**:
  - Don't add unnecessary dependencies
  - Don't create complex build scripts

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple file creation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 3-6, 10)
  - **Blocks**: All implementation tasks
  - **Blocked By**: Task 1 (needs src/ structure first)

  **References**:
  - Dependencies identified: customtkinter, pywin32 (win32gui, win32con, win32event), screeninfo, pystray, Pillow, winshell, pyinstaller

  **Acceptance Criteria**:
  - [ ] `requirements.txt` exists with all dependencies
  - [ ] `pip install -r requirements.txt` succeeds
  - [ ] `config.json` exists with initial structure

  **QA Scenarios**:
  ```
  Scenario: Verify requirements.txt content
    Tool: Bash
    Steps:
      1. cat requirements.txt
      2. grep for each dependency name
    Expected Result: All dependencies listed
    Evidence: .sisyphus/evidence/task-02-requirements.txt

  Scenario: Verify pip install works
    Tool: Bash
    Steps:
      1. pip install -r requirements.txt
      2. pip show customtkinter
    Expected Result: All packages installed
    Evidence: .sisyphus/evidence/task-02-install.log
  ```

  **Commit**: YES
  - Message: `feat: add requirements.txt with dependencies`
  - Files: requirements.txt, config.json

- [x] 3. Config Manager Module

  **What to do**:
  - Create `src/browser_move/config.py` module
  - Implement JSON config read/write with atomic writes (write to .tmp, then rename)
  - Config path: Use `Path(__file__).parent.parent.parent / "config.json"` for project root
  - Config structure: presets array, theme setting, auto-start flag
  - Each preset: name, browser_type, browser_path, url, kiosk_mode

  **Must NOT do**:
  - Don't use pickle or other serialization formats
  - Don't hardcode config path (use relative path)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple utility module
  - **Skills**: []

**Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 4-6, 10)
  - **Blocks**: Tasks 11, 12, 16 (need config)
  - **Blocked By**: Task 1 (needs src/ structure first)

  **References**:
  - Atomic writes: Write to .tmp file, then os.replace() to rename
  - Config location: Project root (portable)

  **Acceptance Criteria**:
  - [ ] `src/browser_move/config.py` exists
  - [ ] `load_config()` returns dict with presets array
  - [ ] `save_config(data)` writes atomically
  - [ ] Config persists after app restart

  **QA Scenarios**:
  ```
  Scenario: Load config returns correct structure
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.config import load_config; c = load_config(); print(list(c.keys()))"
    Expected Result: Output contains 'presets', 'theme', 'auto_start'
    Evidence: .sisyphus/evidence/task-03-config-load.txt

  Scenario: Save config persists data
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.config import save_config, load_config; save_config({'presets': [{'name': 'test'}]}); c = load_config(); print(len(c['presets']))"
    Expected Result: Output shows 1 preset
    Evidence: .sisyphus/evidence/task-03-config-save.txt
  ```

  **Commit**: YES
  - Message: `feat: add JSON config manager`
  - Files: src/browser_move/config.py

- [x] 4. Monitor Detection Module

  **What to do**:
  - Create `src/browser_move/monitors.py` module
  - Use `screeninfo.get_monitors()` to get monitor list
  - Implement `get_primary_monitor()` and `get_external_monitors()`
  - Handle case when no external monitor exists (return empty list)
  - Return monitor objects with x, y, width, height coordinates
  - Add `select_external_monitor()` for multiple external monitors case

  **Must NOT do**:
  - Don't use Win32 API directly (screeninfo is simpler)
  - Don't assume always 1 external monitor

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple wrapper module
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-3, 5-6, 10)
  - **Blocks**: Tasks 9, 11 (need monitor info)
  - **Blocked By**: Task 1 (needs src/ structure first)

  **References**:
  - screeninfo library returns Monitor objects with x, y, width, height, is_primary

  **Acceptance Criteria**:
  - [ ] `src/browser_move/monitors.py` exists
  - [ ] `get_external_monitors()` returns list of non-primary monitors
  - [ ] Works correctly on multi-monitor setup

  **QA Scenarios**:
  ```
  Scenario: Detect monitors correctly
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.monitors import get_external_monitors; ext = get_external_monitors(); print(f'External: {len(ext)}')"
    Expected Result: Shows correct number of external monitors
    Evidence: .sisyphus/evidence/task-04-monitor-detect.txt

  Scenario: No external monitor case
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.monitors import get_external_monitors; print(get_external_monitors())"
    Expected Result: Empty list if no external, no crash
    Evidence: .sisyphus/evidence/task-04-no-external.txt
  ```

  **Commit**: YES
  - Message: `feat: add monitor detection module`
  - Files: src/browser_move/monitors.py

- [x] 5. Browser Path Detection Module

  **What to do**:
  - Create `src/browser_move/browsers.py` module with path detection section
  - Implement `detect_browser_path(browser_type)` for Firefox, Chrome, Edge
  - Firefox: Check `C:\Program Files\Mozilla Firefox\firefox.exe` and `C:\Program Files (x86)\...`
  - Chrome: Check `C:\Program Files\Google\Chrome\Application\chrome.exe`
  - Edge: Check `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
  - Return None if browser not found, allow custom path override
  - Add `BROWSER_PATHS` dict for default paths

  **Must NOT do**:
  - Don't use registry to find paths (hardcoded paths simpler for this use case)
  - Don't auto-install browsers

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple path checking utility
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-4, 6, 10)
  - **Blocks**: Task 7 (needs browser path)
  - **Blocked By**: Task 1 (needs src/ structure first)

  **References**:
  - Existing solution uses Firefox at `C:\Program Files\Mozilla Firefox\firefox.exe`

  **Acceptance Criteria**:
  - [ ] `src/browser_move/browsers.py` exists with `detect_browser_path()` function
  - [ ] Returns correct path for Firefox if installed
  - [ ] Returns None for uninstalled browser

  **QA Scenarios**:
  ```
  Scenario: Detect Firefox path
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.browsers import detect_browser_path; print(detect_browser_path('firefox'))"
    Expected Result: Returns path string or None
    Evidence: .sisyphus/evidence/task-05-browser-path.txt
  ```

  **Commit**: YES
  - Message: `feat: add browser path detection`
  - Files: src/browser_move/browsers.py

- [x] 6. Application Icon Setup

  **What to do**:
  - Create or source a simple icon file `icon.ico` in project root (not in src/)
  - Icon will be used for: system tray, window icon, shortcuts, exe icon
  - Use simple design (browser + monitor visual) or generic app icon
  - Size: 256x256 for exe, 16x16/32x32 for tray

  **Must NOT do**:
  - Don't create complex/animated icon
  - Don't use copyrighted images
  - Don't put icon in src/ folder (should be in project root for exe build)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single asset file creation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-5, 10)
  - **Blocks**: Tasks 15, 19 (need icon for tray/spec)
  - **Blocked By**: None (icon independent of src/ structure)

  **References**:
  - Icon location: Project root for PyInstaller to find
  - ICO format: Multi-resolution icon for Windows

  **Acceptance Criteria**:
  - [ ] `icon.ico` file exists in project root
  - [ ] File is valid ICO format

  **QA Scenarios**:
  ```
  Scenario: Verify icon file exists
    Tool: Bash
    Steps:
      1. ls icon.ico
      2. file icon.ico (if available)
    Expected Result: File exists, valid ICO format
    Evidence: .sisyphus/evidence/task-06-icon.txt
  ```

  **Commit**: YES
  - Message: `feat: add application icon`
  - Files: icon.ico

- [x] 7. Browser Launcher Module

  **What to do**:
  - Add to `src/browser_move/browsers.py`: `launch_browser(browser_type, url, kiosk_mode, browser_path)`
  - Firefox kiosk: `--new-window --kiosk="url"`
  - Chrome kiosk: `--kiosk --app="url"`
  - Edge kiosk: `--kiosk url`
  - Normal mode: just URL argument
  - Return subprocess.Popen object for process tracking

  **Must NOT do**:
  - Don't launch browser synchronously (use subprocess.Popen)
  - Don't hardcode URL in function

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Browser launch logic with multiple modes requires care
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2A (SEQUENTIAL - first in Wave 2)
  - **Blocks**: Task 8 (needs browser launched)
  - **Blocked By**: Task 5 (needs browser path detection)

  **References**:
  - Firefox kiosk: `--new-window --kiosk="url"`
  - Chrome kiosk: `--kiosk --app="url"`
  - Edge kiosk: `--kiosk url`

  **Acceptance Criteria**:
  - [ ] `launch_browser()` function in browsers.py
  - [ ] Browser launches with correct URL
  - [ ] Kiosk mode works for all browsers
  - [ ] Returns subprocess object

  **QA Scenarios**:
  ```
  Scenario: Launch Firefox in normal mode
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.browsers import launch_browser; proc = launch_browser('firefox', 'http://example.com', False); print(proc.pid)"
      2. sleep 2, check Firefox process
    Expected Result: Browser opens, PID returned
    Evidence: .sisyphus/evidence/task-07-launch-normal.txt

  Scenario: Launch Firefox in kiosk mode
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.browsers import launch_browser; launch_browser('firefox', 'http://example.com', True)"
      2. sleep 3, verify fullscreen
    Expected Result: Browser fullscreen, no address bar
    Evidence: .sisyphus/evidence/task-07-launch-kiosk.txt
  ```

  **Commit**: YES
  - Message: `feat: add browser launcher`
  - Files: src/browser_move/browsers.py

- [x] 8. Window Finder Module

  **What to do**:
  - Create `src/browser_move/window_mover.py` with window finding section
  - Implement `find_browser_window(browser_type)` using `win32gui.EnumWindows`
  - Firefox: Look for `MozillaWindowClass` class name
  - Chrome/Edge: Look for `Chrome_WidgetWindow_` class name
  - Return window handle (hwnd) or None if not found
  - Handle timeout: retry loop up to 10 seconds with exponential backoff

  **Must NOT do**:
  - Don't use `FindWindow` (brittle with dynamic titles)
  - Don't assume window appears instantly

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Window enumeration requires careful implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2B (SEQUENTIAL - second in Wave 2)
  - **Blocks**: Task 9 (needs window hwnd)
  - **Blocked By**: Task 7 (needs browser launched first - sequential dependency)

  **References**:
  - Browser class names: Firefox=`MozillaWindowClass`, Chrome/Edge=`Chrome_WidgetWindow_`
  - EnumWindows callback pattern

  **Acceptance Criteria**:
  - [ ] `find_browser_window()` function exists
  - [ ] Returns hwnd for launched browser
  - [ ] Returns None if window not found within timeout

  **QA Scenarios**:
  ```
  Scenario: Find Firefox window after launch
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.browsers import launch_browser; from src.browser_move.window_mover import find_browser_window; launch_browser('firefox', 'http://example.com', False); hwnd = find_browser_window('firefox'); print(hwnd)"
    Expected Result: Returns non-zero hwnd integer
    Evidence: .sisyphus/evidence/task-08-find-window.txt

  Scenario: Timeout when no browser
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.window_mover import find_browser_window; hwnd = find_browser_window('firefox'); print(hwnd)"
    Expected Result: Returns None after timeout
    Evidence: .sisyphus/evidence/task-08-timeout.txt
  ```

  **Commit**: YES
  - Message: `feat: add window finder`
  - Files: src/browser_move/window_mover.py

- [x] 9. Window Mover Module

  **What to do**:
  - Complete `src/browser_move/window_mover.py`: `move_window_to_monitor(hwnd, monitor)`
  - Use `win32gui.SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOZORDER | SWP_NOACTIVATE)`
  - Check if window is maximized, restore first with `ShowWindow(hwnd, SW_RESTORE)`
  - After moving, maximize window on target monitor
  - Handle invalid hwnd (return False)
  - Add `move_browser_to_external(browser_type)` convenience function

  **Must NOT do**:
  - Don't use `MoveWindow` (SetWindowPos is better)
  - Don't move from non-GUI threads
  - Don't skip maximize restore step

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Window manipulation requires careful Win32 API usage
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2C (SEQUENTIAL - third in Wave 2)
  - **Blocks**: Task 18 (integration)
  - **Blocked By**: Task 4 (monitor detection), Task 8 (window hwnd - sequential)

  **References**:
  - SetWindowPos flags: `SWP_NOZORDER | SWP_NOACTIVATE` (0x0004 | 0x0010)
  - Must restore maximized windows before moving

  **Acceptance Criteria**:
  - [ ] `move_window_to_monitor()` function exists
  - [ ] Window moves to correct monitor coordinates
  - [ ] Window maximizes on target monitor

  **QA Scenarios**:
  ```
  Scenario: Move window to external monitor
    Tool: Bash (Python REPL)
    Steps:
      1. Launch browser, find hwnd
      2. Get external monitor
      3. Move window
      4. Verify position matches monitor
    Expected Result: Window on external monitor, maximized
    Evidence: .sisyphus/evidence/task-09-move-window.txt
  ```

  **Commit**: YES
  - Message: `feat: add window mover`
  - Files: src/browser_move/window_mover.py

- [x] 10. DPI Awareness Setup

  **What to do**:
  - Create `src/browser_move/dpi.py` module
  - Use `ctypes.windll.shcore.SetProcessDpiAwareness(2)` for Per-Monitor DPI awareness
  - Call this at app startup BEFORE any window operations
  - Add fallback for older Windows versions (try/except)
  - This ensures accurate monitor coordinates on high-DPI displays

  **Must NOT do**:
  - Don't call after windows are created
  - Don't use older DPI awareness methods

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple ctypes call with fallback
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-6) - standalone, no dependencies
  - **Blocks**: Task 18 (used in entry point)
  - **Blocked By**: Task 1 (needs src/ structure first)

  **References**:
  - DPI awareness value 2 = Per-Monitor DPI Awareness
  - Fallback for Windows versions without shcore

  **Acceptance Criteria**:
  - [ ] `src/browser_move/dpi.py` exists with `setup_dpi_awareness()` function
  - [ ] Function sets Per-Monitor DPI awareness
  - [ ] Handles errors gracefully on older Windows

  **QA Scenarios**:
  ```
  Scenario: DPI awareness set correctly
    Tool: Bash (Python REPL)
    Steps:
      1. python -c "from src.browser_move.dpi import setup_dpi_awareness; setup_dpi_awareness(); print('DPI set')"
    Expected Result: No error, DPI awareness enabled
    Evidence: .sisyphus/evidence/task-10-dpi.txt
  ```

  **Commit**: YES
  - Message: `feat: add DPI awareness setup`
  - Files: src/browser_move/dpi.py

- [x] 11. Main GUI Window

  **What to do**:
  - Create `src/browser_move/app.py` with main CustomTkinter window
  - Set theme BEFORE creating window: `ctk.set_default_color_theme("blue")`
  - Create `CTk()` root window with title "Browser Move Automation"
  - Layout: preset list (left), action buttons (right), status bar (bottom)
  - Add preset selection CTkComboBox
  - Add "Run Preset", "New Preset", "Settings" buttons
  - Implement minimize to tray on close button (WM_DELETE_WINDOW protocol)
  - Main window class should accept tray reference for integration

  **Must NOT do**:
  - Don't create widgets before setting theme
  - Don't exit app on close button (minimize to tray)
  - Don't use overly complex layout

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: GUI design requires visual/engineering skill
  - **Skills**: [`frontend-ui-ux`]
    - For creating clean, modern UI layout

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3A (SEQUENTIAL - first in Wave 3, creates main window)
  - **Blocks**: Tasks 12-15 (need main window reference)
  - **Blocked By**: Task 1 (structure), Task 3 (config), Task 4 (monitor)

  **References**:
  - Theme must be set BEFORE creating widgets
  - CTkComboBox for preset selection, CTkButton for actions

  **Acceptance Criteria**:
  - [ ] `src/browser_move/app.py` exists with `MainWindow` class
  - [ ] Window displays preset list
  - [ ] Window has Run/New/Settings buttons
  - [ ] Theme set before window creation

  **QA Scenarios**:
  ```
  Scenario: Main window displays correctly
    Tool: Bash (Python)
    Steps:
      1. python -c "import customtkinter as ctk; from src.browser_move.app import MainWindow; ctk.set_default_color_theme('blue'); root = ctk.CTk(); app = MainWindow(root); root.mainloop()"
      2. Screenshot capture
    Expected Result: Window opens, buttons visible, modern theme
    Evidence: .sisyphus/evidence/task-11-main-window.png
  ```

  **Commit**: YES
  - Message: `feat: add main GUI window`
  - Files: src/browser_move/app.py

- [x] 12. Preset Form Component

  **What to do**:
  - Create `src/browser_move/preset_form.py` with preset management UI
  - Add Preset: Name entry, Browser dropdown (Firefox/Chrome/Edge), URL entry, Path entry (optional), Kiosk checkbox, Save button
  - Edit Preset: Same fields, Update button, Delete button with confirmation
  - Preset list stored in config.json via config module
  - Validate URL format before saving (regex for http/https)
  - Create modal CTkToplevel for form

  **Must NOT do**:
  - Don't allow duplicate preset names
  - Don't save without validating URL format
  - Don't use non-modal window for form

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Form design requires UI skill
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3B (with Tasks 13-14) - after Task 11 completes
  - **Blocks**: Task 18 (integration)
  - **Blocked By**: Task 3 (config), Task 11 (main window - sequential dependency)

  **References**:
  - CTkEntry for text inputs, CTkComboBox for dropdown, CTkCheckBox for toggle
  - CTkToplevel with grab_set() for modal

  **Acceptance Criteria**:
  - [ ] `src/browser_move/preset_form.py` exists
  - [ ] Add/Edit/Delete preset functionality works
  - [ ] Presets saved to config.json
  - [ ] URL validation before save

  **QA Scenarios**:
  ```
  Scenario: Add new preset
    Tool: Bash (Python)
    Steps:
      1. Launch app, click "New Preset"
      2. Fill: name="Test", browser="Firefox", url="http://test.com"
      3. Save, check config.json
    Expected Result: Preset added to config
    Evidence: .sisyphus/evidence/task-12-add-preset.txt

  Scenario: Delete preset with confirmation
    Tool: Bash (Python)
    Steps:
      1. Launch app with existing preset
      2. Select preset, click Delete, confirm
      3. Check config.json
    Expected Result: Preset removed
    Evidence: .sisyphus/evidence/task-12-delete-preset.txt
  ```

  **Commit**: YES
  - Message: `feat: add preset form component`
  - Files: src/browser_move/preset_form.py

- [x] 13. Settings Window

  **What to do**:
  - Create `src/browser_move/settings_window.py` with CTkToplevel modal
  - Settings: Theme dropdown (Dark/Light/System), Auto-start checkbox, Close behavior dropdown (Exit/Minimize to Tray)
  - Use `grab_set()` for modal behavior
  - Save settings to config.json on Apply button
  - Include "Create Desktop Shortcut" and "Add to Startup" buttons

  **Must NOT do**:
  - Don't use regular window (must be modal)
  - Don't forget `grab_release()` before destroy
  - Don't apply settings without saving to config

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Settings dialog design
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3B (with Tasks 12, 14) - after Task 11 completes
  - **Blocks**: None (settings optional)
  - **Blocked By**: Task 11 (main window - sequential dependency)

  **References**:
  - CTkToplevel with grab_set() for modal
  - CustomTkinter appearance_mode: "Dark", "Light", "System"

  **Acceptance Criteria**:
  - [ ] `src/browser_move/settings_window.py` exists
  - [ ] Settings modal opens from main window
  - [ ] Theme changes applied correctly
  - [ ] Shortcut buttons included

  **QA Scenarios**:
  ```
  Scenario: Settings window opens as modal
    Tool: Bash (Python)
    Steps:
      1. Launch app, open Settings
      2. Verify main window blocked
    Expected Result: Settings modal, main blocked
    Evidence: .sisyphus/evidence/task-13-settings-modal.png
  ```

  **Commit**: YES
  - Message: `feat: add settings window`
  - Files: src/browser_move/settings_window.py

- [x] 14. Status Bar Component

  **What to do**:
  - Create `src/browser_move/status_bar.py` with status display
  - Show: current status (Ready/Running/Error), last action time
  - Color indicator: Green=Ready, Orange=Running, Red=Error
  - Update status via callback from main window
  - Include log of recent actions (optional)

  **Must NOT do**:
  - Don't block main thread with status updates
  - Don't use complex progress bars

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Status UI component
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3B (with Tasks 12-13) - after Task 11 completes
  - **Blocks**: None
  - **Blocked By**: Task 11 (main window - sequential dependency)

  **References**:
  - CTkLabel with colored text for status

  **Acceptance Criteria**:
  - [ ] `src/browser_move/status_bar.py` exists
  - [ ] Status displays Ready/Running/Error states
  - [ ] Color changes based on state

  **QA Scenarios**:
  ```
  Scenario: Status bar shows correct state
    Tool: Bash (Python)
    Steps:
      1. Launch app, run preset
      2. Verify status changes Ready → Running → Ready
    Expected Result: Status changes dynamically
    Evidence: .sisyphus/evidence/task-14-status.txt
  ```

  **Commit**: YES
  - Message: `feat: add status bar component`
  - Files: src/browser_move/status_bar.py

- [x] 15. System Tray Integration

  **What to do**:
  - Create `src/browser_move/tray.py` with pystray integration
  - Create tray icon using `icon.ico` from project root
  - Menu items: Show Window, Run Preset (submenu with preset names), Settings, Exit
  - Use `pystray.Icon("BrowserMove", image, menu).run_detached()`
  - Integrate with main window hide/show via callbacks
  - Handle double-click to show window

  **Must NOT do**:
  - Don't run pystray on main thread (blocks GUI)
  - Don't use large icon files
  - Don't create complex nested menus

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: System tray integration requires threading care
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 16-17)
  - **Blocks**: None
  - **Blocked By**: Task 6 (icon), Task 11 (main window)

  **References**:
  - pystray.run_detached() is safe on Windows
  - Menu: pystray.Menu with pystray.MenuItem

  **Acceptance Criteria**:
  - [ ] `src/browser_move/tray.py` exists
  - [ ] Tray icon visible when app runs
  - [ ] Menu shows presets and options
  - [ ] Clicking "Show Window" restores main window

  **QA Scenarios**:
  ```
  Scenario: Tray icon visible
    Tool: Bash (Python)
    Steps:
      1. Launch app, minimize window
      2. Check system tray for icon
    Expected Result: Icon in system tray
    Evidence: .sisyphus/evidence/task-15-tray-icon.png

  Scenario: Tray menu shows presets
    Tool: Bash (Python)
    Steps:
      1. Right-click tray icon
      2. Verify preset names in menu
    Expected Result: Presets in submenu
    Evidence: .sisyphus/evidence/task-15-tray-menu.png
  ```

  **Commit**: YES
  - Message: `feat: add system tray integration`
  - Files: src/browser_move/tray.py

- [x] 16. Shortcut Creation Module

  **What to do**:
  - Create `src/browser_move/shortcuts.py` module
  - Implement `create_desktop_shortcut(preset_name)` using `winshell.CreateShortcut`
  - Implement `add_to_startup()` - copy shortcut to Startup folder
  - Implement `remove_from_startup()` - delete from Startup folder
  - Shortcut target: `pythonw.exe -m browser_move.main --preset "name"` or exe path
  - Startup folder: Use `winshell.folder("startup")`

  **Must NOT do**:
  - Don't modify registry for startup
  - Don't create shortcuts without user confirmation
  - Don't use hardcoded paths for Startup folder

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Windows shortcut API usage
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 15, 17)
  - **Blocks**: None
  - **Blocked By**: Task 3 (config for auto-start flag)

  **References**:
  - winshell.CreateShortcut(Path=..., Target=..., Arguments=...)
  - winshell.folder("startup") for Startup folder path

  **Acceptance Criteria**:
  - [ ] `src/browser_move/shortcuts.py` exists
  - [ ] Desktop shortcut created successfully
  - [ ] Startup shortcut adds/removes correctly

  **QA Scenarios**:
  ```
  Scenario: Create desktop shortcut
    Tool: Bash (Python + PowerShell)
    Steps:
      1. python -c "from src.browser_move.shortcuts import create_desktop_shortcut; create_desktop_shortcut('Test')"
      2. Test-Path "$env:USERPROFILE\Desktop\Test.lnk"
    Expected Result: Shortcut on Desktop
    Evidence: .sisyphus/evidence/task-16-desktop.txt

  Scenario: Add to startup folder
    Tool: Bash (Python + PowerShell)
    Steps:
      1. python -c "from src.browser_move.shortcuts import add_to_startup; add_to_startup()"
      2. Test-Path "$env:APPDATA\...\Startup\BrowserMove.lnk"
    Expected Result: Shortcut in Startup
    Evidence: .sisyphus/evidence/task-16-startup.txt
  ```

  **Commit**: YES
  - Message: `feat: add shortcut creation module`
  - Files: src/browser_move/shortcuts.py

- [x] 17. Single Instance Lock

  **What to do**:
  - Create `src/browser_move/single_instance.py` module
  - Use `win32event.CreateMutex(None, False, "BrowserMoveAppMutex")`
  - Check if mutex already exists - if yes, show message and exit
  - Return True if we got the lock, False if another instance exists
  - Call at app startup before creating main window
  - Release mutex on app exit (optional, Windows handles it)

  **Must NOT do**:
  - Don't allow multiple instances running simultaneously
  - Don't use file-based locking (mutex is cleaner)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple mutex implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 15-16)
  - **Blocks**: Task 18 (entry point needs this)
  - **Blocked By**: Task 1 (needs src/ structure first)

  **References**:
  - win32event.CreateMutex with named mutex
  - GetLastError() to check if mutex already exists

  **Acceptance Criteria**:
  - [ ] `src/browser_move/single_instance.py` exists
  - [ ] `check_single_instance()` returns True/False
  - [ ] Second instance exits gracefully

  **QA Scenarios**:
  ```
  Scenario: Single instance prevents duplicate
    Tool: Bash (Python)
    Steps:
      1. Launch app (first instance)
      2. Launch app again (second)
      3. Verify second exits
    Expected Result: Only one instance
    Evidence: .sisyphus/evidence/task-17-single-instance.txt
  ```

  **Commit**: YES
  - Message: `feat: add single instance lock`
  - Files: src/browser_move/single_instance.py

- [x] 18. Entry Point Integration

  **What to do**:
  - Create `src/browser_move/main.py` as entry point
  - Flow: setup DPI → check single instance → load config → setup tray → create main window → run
  - Handle `--preset "name"` CLI argument for direct preset execution
  - Handle `--headless` CLI argument for background mode (tray only)
  - Integrate all modules
  - Run tray in detached mode, then CustomTkinter mainloop
  - Ensure proper shutdown sequence

  **Must NOT do**:
  - Don't skip DPI setup or single instance check
  - Don't create window before tray setup
  - Don't use blocking calls in wrong order

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Integration requires understanding all modules
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 5 (SEQUENTIAL - integrates all modules)
  - **Blocks**: Tasks 19, 20 (need entry point)
  - **Blocked By**: Tasks 1-17 (all previous modules must complete)

  **References**:
  - All modules must be imported and integrated

  **Acceptance Criteria**:
  - [ ] `src/browser_move/main.py` exists
  - [ ] App launches successfully with all features
  - [ ] CLI arguments work
  - [ ] Full workflow functional

  **QA Scenarios**:
  ```
  Scenario: Full app launch and preset execution
    Tool: Bash (Python)
    Steps:
      1. python -m src.browser_move.main
      2. Wait for GUI, select preset, click Run
      3. Verify browser moves to external monitor
    Expected Result: Browser on external monitor
    Evidence: .sisyphus/evidence/task-18-full-run.png

  Scenario: CLI preset execution
    Tool: Bash (Python)
    Steps:
      1. python -m src.browser_move.main --preset "Test" --headless
      2. Verify browser launches without GUI
    Expected Result: Browser launched, tray visible
    Evidence: .sisyphus/evidence/task-18-cli-run.txt

  Scenario: Error handling - no external monitor
    Tool: Bash (Python)
    Steps:
      1. Disconnect external, run preset
      2. Verify error dialog shown
    Expected Result: Error shown, app continues
    Evidence: .sisyphus/evidence/task-18-no-monitor-error.png
  ```

  **Commit**: YES
  - Message: `feat: integrate all modules in entry point`
  - Files: src/browser_move/main.py

- [x] 19. PyInstaller Spec File

  **What to do**:
  - Create `browser_move.spec` in project root for PyInstaller
  - Configure --onedir mode (directory distribution)
  - Configure --windowed (no console window for GUI app)
  - Include icon.ico as application icon
  - Include all data files: icon.ico, config.json (if exists)
  - Set entry point: src.browser_move.main:main or similar
  - Hidden imports: customtkinter, pystray, winshell, screeninfo, win32gui, win32con, win32event

  **Must NOT do**:
  - Don't use --onefile (user wants --onedir)
  - Don't include unnecessary files in bundle
  - Don't forget hidden imports for pywin32

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single config file creation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 6 (with Task 20) - after Task 18 completes
  - **Blocks**: Final verification (exe build test)
  - **Blocked By**: Task 18 (entry point), Task 6 (icon)

  **References**:
  - PyInstaller spec file format with Analysis, COLLECT steps
  - --onedir creates dist/browser_move/ folder

  **Acceptance Criteria**:
  - [ ] `browser_move.spec` exists
  - [ ] `pyinstaller browser_move.spec` succeeds
  - [ ] Exe runs standalone

  **QA Scenarios**:
  ```
  Scenario: Build exe successfully
    Tool: Bash
    Steps:
      1. pyinstaller browser_move.spec
      2. ls dist/browser_move/
    Expected Result: dist/browser_move/browser_move.exe exists
    Evidence: .sisyphus/evidence/task-19-build.txt

  Scenario: Exe runs standalone
    Tool: Bash
    Steps:
      1. ./dist/browser_move/browser_move.exe
      2. Verify GUI appears without Python
    Expected Result: App runs without Python installed
    Evidence: .sisyphus/evidence/task-19-exe-run.png
  ```

  **Commit**: YES
  - Message: `feat: add PyInstaller spec file for exe build`
  - Files: browser_move.spec

- [x] 20. README Documentation

  **What to do**:
  - Create `README.md` with project documentation
  - Include: Project description, Features list, Installation (dev mode), Usage (GUI + CLI), Build instructions (PyInstaller), Configuration (config.json structure), Screenshots (optional)
  - Document CLI arguments: --preset, --headless
  - Document preset configuration fields
  - Add usage examples

  **Must NOT do**:
  - Don't create overly complex documentation
  - Don't skip build instructions

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Documentation requires writing skill
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 6 (with Task 19) - after implementation complete
  - **Blocks**: None
  - **Blocked By**: None (can write anytime, but best after Task 18 for accurate docs)

  **References**:
  - Standard README format: Description, Installation, Usage, Build

  **Acceptance Criteria**:
  - [ ] `README.md` exists
  - [ ] Includes installation instructions
  - [ ] Includes usage examples
  - [ ] Includes build instructions

  **QA Scenarios**:
  ```
  Scenario: README has required sections
    Tool: Bash
    Steps:
      1. grep "Installation" README.md
      2. grep "Usage" README.md
      3. grep "Build" README.md
    Expected Result: All sections present
    Evidence: .sisyphus/evidence/task-20-readme.txt
  ```

  **Commit**: YES
  - Message: `docs: add README documentation`
  - Files: README.md

---

## Final Verification Wave (MANDATORY)

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. Verify all "Must Have" items implemented. Check evidence files exist.

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run Python linting (pylint/flake8). Check for AI slop patterns. Check src/ structure is correct.

- [x] F3. **Real Manual QA + Exe Build** — `unspecified-high`
  Start app clean. Execute every QA scenario. Build exe with PyInstaller. Verify exe runs standalone.

- [x] F4. **Scope Fidelity Check** — `deep`
  Verify implementation matches plan exactly. No scope creep. Verify src/ layout structure.

---

## Commit Strategy

- **1**: `feat: initialize project with src/ layout and pyproject.toml`
- **2**: `feat: add requirements.txt with dependencies`
- **3**: `feat: add JSON config manager`
- **4**: `feat: add monitor detection module`
- **5**: `feat: add browser path detection`
- **6**: `feat: add application icon`
- **7**: `feat: add browser launcher`
- **8**: `feat: add window finder`
- **9**: `feat: add window mover`
- **10**: `feat: add DPI awareness setup`
- **11**: `feat: add main GUI window`
- **12**: `feat: add preset form component`
- **13**: `feat: add settings window`
- **14**: `feat: add status bar component`
- **15**: `feat: add system tray integration`
- **16**: `feat: add shortcut creation module`
- **17**: `feat: add single instance lock`
- **18**: `feat: integrate all modules in entry point`
- **19**: `feat: add PyInstaller spec file for exe build`
- **20**: `docs: add README documentation`

---

## Success Criteria

### Verification Commands
```bash
# Verify Python environment
python --version  # Expected: Python 3.x

# Verify project structure
ls src/browser_move/  # Expected: module files present

# Verify dependencies installed
pip install -e .  # Expected: package installed in editable mode

# Verify config file exists
cat config.json  # Expected: JSON with presets array

# Launch application (dev mode)
python -m browser_move.main  # Expected: GUI window appears

# Build exe
pyinstaller browser_move.spec  # Expected: dist/browser_move/ folder created

# Run exe
./dist/browser_move/browser_move.exe  # Expected: GUI runs without Python
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] src/ layout structure correct
- [ ] Application runs without errors
- [ ] GUI displays correctly
- [ ] Browser moves to external monitor
- [ ] System tray icon visible
- [ ] Shortcuts created successfully
- [ ] Exe builds and runs standalone