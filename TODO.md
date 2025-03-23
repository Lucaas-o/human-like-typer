# Human-like Typer To-Do List
*Last Updated: March 23, 2025*  
*Purpose: Suggestions for enhancing functionality, usability, and realism of the Human-like Typer program*

## Core Features

### 1. Custom Hotkey Configuration
- [ ] Add an option in the config menu to set a custom pause/resume hotkey.
  - **Details**: 
    - Extend `config.json` to include a "hotkey" field (e.g., `{"hotkey": "p"}`).
    - Update `configure()` to prompt for a hotkey input (validate using `pynput` syntax).
    - Modify `main_menu()` to use the stored hotkey dynamically.
  - **Benefit**: Allows users to choose a hotkey that suits their workflow.
  - **Note**: Simplified to 'p' in v1.3.1; make configurable next.

### 2. User-Editable Config Profiles
- [ ] Allow users to save and switch between different configurations (e.g., "work", "personal").
  - **Details**:
    - Add a profile management system in `config.json` (e.g., `"profiles": {"work": {"wpm": 80, ...}}`).
    - Update `configure()` with a "Select Profile" or "Save Profile" option.
    - Load the selected profile at runtime.
  - **Benefit**: Enables quick settings changes without manual reconfiguration.

### 3. Typing Speed Profiles
- [ ] Implement preset profiles (e.g., "beginner", "average", "expert") with WPM, error rates, and cooldowns.
  - **Details**:
    - Define profiles in code (e.g., `{"beginner": {"wpm": 60, "error_prob": 5.0, "cooldown": 5}}`).
    - Add a config menu option (e.g., "Set Profile") to select from presets.
    - Integrate with user-editable profiles for flexibility.
  - **Benefit**: Simplifies setup for common skill levels.

### 4. Realistic Error Patterns
- [ ] Simulate common typos (e.g., "teh" for "the") based on keyboard layout instead of random characters.
  - **Details**:
    - Create a keyboard layout map (e.g., QWERTY) with adjacent key probabilities.
    - In `type_text()`, replace random error character with layout-based mistakes (e.g., 't' -> 'r').
    - Support language-specific layouts (e.g., Spanish ñ placement).
  - **Benefit**: Increases realism by mimicking human typing errors.

### 5. Customizable Typing Patterns
- [ ] Allow fine-tuning of typing behavior.
  - **Details**:
    - Extend `config.json` with options like `"punctuation_delay_factor": 1.5`, `"mistake_frequency": 0.02`.
    - Adjust `type_text()` to use these factors for punctuation and special keys.
    - Simulate occasional mistakes with configurable patterns (e.g., double letters).
  - **Benefit**: Provides more control over typing realism.

### 6. Pause Duration Tracking
- [x] Track time spent paused and subtract it from actual WPM calculation.
  - **Details**:
    - Added global `pause_time` and `pause_start_time`, updated in `on_pause_hotkey()` and `type_text()`.
    - Adjusted `actual_wpm` calculation in `type_text()`: `elapsed_time - total_pause_time`.
    - Displayed pause duration in the completion message (v1.3.1).
  - **Benefit**: Ensures accurate WPM reflecting active typing time.

### 7. Speed Variation Over Time
- [ ] Simulate human fatigue or bursts by varying WPM (e.g., slowing down after 500 characters).
  - **Details**:
    - Add a fatigue factor in `calculate_delays()` (e.g., increase `base_avg_time` by 10% after 500 chars).
    - Implement random bursts (e.g., 20% faster for 50 chars occasionally).
    - Make variation configurable in `config.json`.
  - **Benefit**: Mimics natural human typing patterns.

### 8. Multi-File Support
- [ ] Allow typing multiple files in sequence with a queue system in the "Typer" option.
  - **Details**:
    - Modify `get_text_file_path()` to accept comma-separated paths or a directory.
    - Create a queue (list) of files in `main_menu()` for option 2.
    - Loop through the queue in `type_text()`, processing one file at a time.
  - **Benefit**: Streamlines typing multiple documents without restarting.

## Usability Enhancements

### 9. Graphical Interface
- [ ] Create a simple Tkinter or PyQt interface for a graphical menu.
  - **Details**:
    - Choose a library (e.g., `tkinter` for simplicity, install via `pip install tk` if needed).
    - Design a window with buttons for "Configure", "Type", "Exit".
    - Port `configure()` and `main_menu()` logic to GUI events.
    - Keep console version as an option (e.g., run with `--console` flag).
    - Reintroduce language translations as a dropdown.
  - **Benefit**: Improves accessibility for non-technical users.

### 10. Command-Line Arguments
- [ ] Enable command-line arguments to override settings or start in a specific mode.
  - **Details**:
    - Use `argparse` to support flags (e.g., `--wpm 80`, `--file path/to/file.txt`, `--mode gui`).
    - Update `main_menu()` to parse args and apply them before the loop.
    - Document usage in a `--help` message.
  - **Benefit**: Enhances flexibility for advanced users.

### 11. Advanced Window Targeting
- [ ] Enhance window selection with search and broader app support.
  - **Details**:
    - Allow typing a window title substring to filter options.
    - Expand `get_active_windows()` to detect more apps beyond the current 5 (e.g., Notepad, Word).
    - Add an option to type into hidden/minimized windows without activation.
  - **Benefit**: Increases flexibility for multi-monitor or background use.
  - **Note**: Current `pygetwindow` activation issue (fixed with click fallback in v1.3.2) may need revisiting.

## Audio and Feedback

### 12. Sound Effects
- [ ] Add optional keyboard typing sounds using the `playsound` library.
  - **Details**:
    - Install `playsound` (`pip install playsound`).
    - Source or generate keypress sound files (e.g., `keypress.wav`).
    - In `type_text()`, play sound asynchronously after each batch.
    - Add a config option to enable/disable sounds.
  - **Benefit**: Enhances immersion and realism.

## Logging and Debugging

### 13. Enhanced Logging
- [ ] Implement detailed logging to a file using Python’s `logging` module.
  - **Details**:
    - Replace print statements with `logging` calls (e.g., `logging.info`, `logging.error`).
    - Configure a log file (e.g., `typer.log`) with timestamps and levels (INFO, ERROR).
    - Log events like config changes, typing start/end, and errors.
  - **Benefit**: Aids troubleshooting, especially for compiled executables.

## Additional Notes
- **Priority**: 
  - High: GUI (usability leap), Realistic Error Patterns (realism).
  - Medium: Profiles, Logging (convenience and debugging).
  - Low: Sound Effects, Speed Variation (nice-to-have features).
- **Testing**: 
  - WPM accuracy achieved in v1.4.1; test with larger files and special characters (e.g., ñ, é).
  - Verify hotkey reliability across OSes (Windows, macOS, Linux).
  - Check window targeting on multi-monitor setups.
- **Dependencies**: 
  - Current: `pyautogui`, `pynput`, `psutil`, `pygetwindow`.
  - Future: `tkinter` (GUI), `playsound` (audio), `argparse` (CLI).