# Human-like Typer

A Python script that simulates human-like typing by reading text from a file and typing it into any application with realistic delays. Supports English, Spanish, and French, with configurable typing speed (WPM) and automatic cooldowns after newlines.

## Features
- **Human-like Typing**: Mimics natural typing with random delays between characters and words.
- **Multi-language Support**: Interface in English (`en`), Spanish (`sp`), or French (`fr`).
- **Configurable Settings**: Adjust WPM, language, and newline cooldown, saved in `config.txt`.
- **Text File Input**: Reads from a file, defaults to `text.txt` in the script directory.
- **Pause/Resume**: Press Enter to pause or resume typing.
- **Executable Option**: Includes a pre-built `.exe` for Windows users.

## Requirements
- Python 3.6+ (for running the script).
- PyAutoGUI library (install with `pip install pyautogui`).
- Windows (for the `.exe` version; others can use the `.py` file).

## Installation
1. **Download**: Get the files from this repository.
2. **Install Python** (if running the script): Download from python.org.
3. **Install PyAutoGUI** (if running the script): Run `pip install pyautogui` in a terminal.
4. **Run**: Use `python human_like_typer.py` or double-click `human_like_typer.exe`.

## Usage
1. **Prepare a Text File**:
   - Create `text.txt` in the same folder as the script, or use a custom file.
   - Example `text.txt`:
  Hello, world!
  Bonjour, le monde!
  Hola, mundo!


2. **Run the Program**:
- Start `human_like_typer.py` or `human_like_typer.exe`.
- Menu options:
- **1. Configuration**: Set WPM, language (`en/sp/fr`), and cooldown.
- **2. Typer**: Start typing from the text file.
- **3. Exit**: Quit (with confirmation).

3. **Typing Process**:
- After selecting "Typer," switch to your target window within 3 seconds.
- The script types with human-like delays.
- Press Enter to pause/resume manually.
- After each newline, it pauses for the set cooldown and resumes automatically.

4. **Keyboard Layout**:
- Match your system’s keyboard layout to the text’s language (e.g., Spanish for `ñ`).

## Configuration
Settings are stored in `config.txt`:
  wpm=60.0 / 60 
  language=en/sp/fr
 cooldown=3 (s)

- Edit manually or use the configuration menu.

## Building the .exe
To create your own `.exe`:
1. Install PyInstaller with `pip install pyinstaller`.
2. Build it with `pyinstaller --onefile human_like_typer.py`.
3. Find `human_like_typer.exe` in the `dist` folder.

## Note about .exe
Building the .exe may result in false positives like the ones with this .exe.
`The detections (e.g., "Program:Win32/Wacapew.C!ml," "BehavesLike.Win64.Dropper.wc") are consistent with tools that automate input or file operations, as seen in web discussions about similar false positives (e.g., games or utilities flagged by McAfee for file I/O). Your script’s benign intent and low detection rate (5/72) support the conclusion that it’s safe. Submitting it to VirusTotal for further analysis should help refine these detections over time.`

## Notes
- The `.exe` works on Windows only.
- Ensure your target window is active before typing starts.
- Use Ctrl+C in the terminal to force quit if needed.

## License
Open-source under the MIT License.

## Contributing
Fork, submit issues, or pull requests to improve the project!