# Human-like Typer

A standalone desktop application built in Rust that simulates human-like keyboard input with variable timing, punctuation pauses, optional typo-and-backspace correction, and instant stop control—distributed as a single executable with no Python, Node.js, or external runtime required.

## Features

- **Standalone native executable** – runs without installing Python, runtimes, or third-party packages
- **Human-like timing** – configurable target WPM, timing jitter, and extra pauses on punctuation
- **Optional typo simulation** – occasional nearby-key mistakes corrected with `Backspace`
- **Safe start & stop** – configurable countdown before typing starts and immediate **Stop** button
- **Persistent settings** – saves preferences locally to your OS configuration directory

## Building a Standalone Executable

Requires [Rust](https://rustup.rs/) only on the machine building the binary:

```bash
cargo build --release
```

Output binary:
- **Windows:** `target\release\human-like-typer.exe`
- **macOS / Linux:** `target/release/human-like-typer`

## Usage

1. Launch the executable.
2. Enter or paste the text to type.
3. Adjust **Speed (WPM)**, **Timing jitter (%)**, **Start delay (sec)**, and **typo simulation** as needed.
4. Click **Start Typing** and switch focus to your target input field before the countdown finishes.
5. Click **Stop** at any time to abort typing.

## Troubleshooting

- **macOS:** Grant **Accessibility** permission to the terminal or executable under **System Settings → Privacy & Security → Accessibility**.
- **Linux:** Ensure keyboard input simulation is permitted in your active X11/Wayland session.
- **Antivirus false positives:** Unsigned or newly compiled input-simulation binaries occasionally trigger heuristic alerts; test locally or sign/allowlist as needed.

## License

MIT — see [LICENSE](LICENSE).