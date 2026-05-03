# Human-like Typer

Python utility that simulates human-like typing: per-character timing from a target WPM, random jitter, optional batched typos and corrections, pauses after words and punctuation, and global hotkeys for pause/stop. Ships with a **Tkinter GUI** (default) and a **`--cli` console menu**.

## Requirements

- Python 3.10+ recommended  
- Dependencies: see [`requirements.txt`](requirements.txt) (`pyautogui`, `PyGetWindow`, `pynput`)

```bash
pip install -r requirements.txt
```

## Run

```bash
python human_like_typer.py
```

Opens the graphical interface. Use the **CLI menu** instead:

```bash
python human_like_typer.py --cli
```

### One-shot (no GUI)

```bash
python human_like_typer.py -f path/to/text.txt
```

Focus the target window before the countdown ends, or select it when prompted.

| Flag | Meaning |
|------|---------|
| `--foreground-only` | Do not show the window list; type into the window that already has focus. |
| `--dry-run` | Print timing estimate only; no keystrokes. |
| `-f` / `--file` | Text file (UTF-8). |
| `--wpm N` | Override target WPM for this run. |
| `--countdown SEC` | Delay before typing (default `3`; use `0` to skip). |
| `--save` | With `--wpm`, persist WPM into `config.json`. |

## Controls while typing

- **Pause / resume**: configurable global hotkey (default `<f8>` — see `config.json`).
- **Stop**: configurable (default `<esc>`).
- **Mouse at left or right screen edge** (not top/bottom): pauses for a few seconds (configurable).
- **Mouse in a screen corner**: PyAutoGUI fail-safe — movement stops (if `FAILSAFE` is on).

Set your **system keyboard layout** to match the text (e.g. Spanish for `ñ` and accents). The app’s “language” option only changes typo adjacency maps (English vs Spanish QWERTY).

## Configuration

Settings are stored in **`config.json`** next to `human_like_typer.py` (same folder as the `.exe` if you freeze the app). Defaults include:

- `wpm`, `cooldown` (seconds after newline), `error_prob` (%), `language` (`english` / `spanish`)
- `hotkey_pause`, `hotkey_stop` (pynput-style, e.g. `<f8>`, `<esc>`)
- `mouse_edge_pause`, `mouse_edge_pause_seconds`
- Word pauses: `word_pause_min_ms`, `word_pause_max_ms`
- `punctuation_extra_factor`, thinking pauses (`thinking_pause_*`)
- `fatigue_enabled` / `burst_enabled` and related tuning
- `window_list_limit` (how many windows to show when picking a target)

You can edit the file or use **Configuration** in `--cli` / **Save settings** in the GUI.

## Logging

- Human-readable line log: `typer_log.txt` (session summaries).
- Detailed rotating log: `typer_session.log` (with `-v` / verbose, more detail in the file).

## Building a Windows `.exe` (optional)

```bash
pip install pyinstaller
pyinstaller --onefile human_like_typer.py
```

Some antivirus tools flag auto-typers; that is a known class of false positives for PyInstaller-packaged tools.

## License

MIT License — see [LICENSE](LICENSE).

## Contributing

Issues and pull requests are welcome.
