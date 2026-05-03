import logging
import os

from hltyper import VERSION
from hltyper.config import load_config, merge_defaults, save_config
from hltyper.engine import calculate_delays
from hltyper.paths import get_project_root
from hltyper.session import dry_run_estimate, run_typing_session

logger = logging.getLogger(__name__)


def get_text_file_path_interactive():
    root = get_project_root()
    default_path = os.path.join(root, "text.txt")
    while True:
        path = input(
            "Enter path to text file (Enter for 'text.txt' in script folder): "
        ).strip()
        if not path:
            if os.path.isfile(default_path):
                return default_path
            print(f"Default file not found: {default_path}")
            continue
        if os.path.isfile(path):
            return path
        print("File not found. Try again.")


def configure(cfg: dict) -> None:
    cfg = merge_defaults(cfg)
    while True:
        print(
            f"\n--- Configuration ---\n"
            f"1. WPM (current: {cfg['wpm']})\n"
            f"2. Newline cooldown s (current: {cfg['cooldown']})\n"
            f"3. Error probability % (current: {cfg['error_prob']})\n"
            f"4. Language english/spanish (current: {cfg['language']})\n"
            f"5. Hotkeys: pause / stop (current: {cfg['hotkey_pause']} / {cfg['hotkey_stop']})\n"
            f"6. Window list limit (current: {cfg['window_list_limit']})\n"
            f"7. Human sim: fatigue on/off (current: {cfg['fatigue_enabled']})\n"
            f"8. Human sim: burst typing on/off (current: {cfg['burst_enabled']})\n"
            f"9. Back to main menu"
        )
        choice = input("Select (1-9): ").strip()
        if choice == "1":
            try:
                wpm = float(input("WPM (30-220): "))
                if not 30 <= wpm <= 220:
                    raise ValueError("Out of range.")
                cfg["wpm"] = wpm
                save_config(cfg)
                print("Saved.")
            except ValueError as e:
                print(f"Invalid: {e}")
        elif choice == "2":
            try:
                c = float(input("Cooldown after newline (0-30 s): "))
                if not 0 <= c <= 30:
                    raise ValueError("Out of range.")
                cfg["cooldown"] = c
                save_config(cfg)
                print("Saved.")
            except ValueError as e:
                print(f"Invalid: {e}")
        elif choice == "3":
            try:
                e = float(input("Error probability (0-20 %): "))
                if not 0 <= e <= 20:
                    raise ValueError("Out of range.")
                cfg["error_prob"] = e
                save_config(cfg)
                print("Saved.")
            except ValueError as ex:
                print(f"Invalid: {ex}")
        elif choice == "4":
            lang = input("english or spanish: ").strip().lower()
            if lang in ("english", "spanish"):
                cfg["language"] = lang
                save_config(cfg)
                print("Saved.")
            else:
                print("Invalid.")
        elif choice == "5":
            p = input(f"Pause hotkey (pynput format, e.g. <f8>, current {cfg['hotkey_pause']}): ").strip()
            s = input(f"Stop hotkey (e.g. <esc>, current {cfg['hotkey_stop']}): ").strip()
            if p:
                cfg["hotkey_pause"] = p
            if s:
                cfg["hotkey_stop"] = s
            save_config(cfg)
            print("Saved.")
        elif choice == "6":
            try:
                n = int(input("Max windows to show when picking (5-80): "))
                if not 5 <= n <= 80:
                    raise ValueError("Out of range.")
                cfg["window_list_limit"] = n
                save_config(cfg)
                print("Saved.")
            except ValueError as e:
                print(f"Invalid: {e}")
        elif choice == "7":
            v = input("Enable fatigue slowdown over long text? (y/n): ").strip().lower()
            cfg["fatigue_enabled"] = v == "y"
            save_config(cfg)
            print("Saved.")
        elif choice == "8":
            v = input("Enable occasional burst typing? (y/n): ").strip().lower()
            cfg["burst_enabled"] = v == "y"
            save_config(cfg)
            print("Saved.")
        elif choice == "9":
            break
        else:
            print("Invalid choice.")


def main_menu(cfg: dict) -> None:
    cfg = merge_defaults(cfg)
    root = get_project_root()

    try:
        while True:
            print(
                f"\n--- Human-like Typer v{VERSION} ---\n"
                "1. Configuration\n"
                "2. Type from file\n"
                "3. Exit"
            )
            choice = input("Select (1-3): ").strip()
            if choice == "1":
                configure(cfg)
                cfg = load_config()
            elif choice == "2":
                print(
                    "Use a keyboard layout that matches your text (e.g. Spanish for ñ).\n"
                    "Windows: Settings → Time & Language → Language."
                )
                fg = (
                    input("Type into current window only? (y/n, default n): ")
                    .strip()
                    .lower()
                    == "y"
                )
                path = get_text_file_path_interactive()
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if not content.strip():
                        print("File is empty.")
                        continue
                    avg = calculate_delays(cfg["wpm"], content)
                    print(f"Average delay per character (target): {avg:.4f}s")
                    run_typing_session(
                        file_path=path,
                        cfg=cfg,
                        dry_run=False,
                        foreground_only=fg,
                        pick_window=not fg,
                        countdown=3.0,
                    )
                except OSError as e:
                    print(f"Could not read file: {e}")
            elif choice == "3":
                if input("Exit? (y/n): ").strip().lower() == "y":
                    print("Goodbye.")
                    break
            else:
                print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nInterrupted.")


def run_cli_main(cfg: dict) -> None:
    main_menu(cfg)
