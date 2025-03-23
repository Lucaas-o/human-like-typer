import pyautogui
import time
import random
import threading
import os
import sys
import json
import string
from pynput import keyboard
from datetime import datetime
import psutil  # For window detection
import pygetwindow as gw  # For window management

# Script metadata
VERSION = "1.4.1"  # Batch typing and WPM fix

def get_script_directory():
    """Get the directory where the script or executable is running."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

script_dir = get_script_directory()
config_path = os.path.join(script_dir, "config.json")
log_path = os.path.join(script_dir, "typer_log.txt")

# Constants
ERROR_CORRECTION_DELAY = 0.1
POST_CORRECTION_DELAY = 0.05
SPACE_DELAY_RANGE = (0.05, 0.15)
BATCH_SIZE = 5  # Number of characters to type in one go

# Global variables
pause_event = threading.Event()
typing_start_time = 0
total_chars_typed = 0
pause_start_time = 0
total_pause_time = 0
config = {}

def load_config():
    """Load the config file or create a default one."""
    default_config = {"wpm": 60, "cooldown": 3, "error_prob": 1.0}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading config file: {e}. Using defaults.")
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(default_config, file, indent=4)
    return default_config

def save_config(config):
    """Save configuration to config.json."""
    try:
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def log_typing_session(file_path, chars, wpm):
    """Log typing session to a file."""
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"Typed {chars} characters from {file_path} at {wpm:.1f} WPM on {date}"
            log_file.write(f"{entry}\n")
    except Exception as e:
        print(f"Error writing to log: {e}")

def get_text_file_path():
    """Get and validate the text file path."""
    default_path = os.path.join(script_dir, "text.txt")
    while True:
        path = input("Enter the path to the text file (or press Enter for 'text.txt'): ").strip()
        if not path and os.path.exists(default_path):
            return default_path
        elif os.path.exists(path) and os.path.isfile(path):
            return path
        print("File not found or inaccessible. Please try again.")

def get_active_windows():
    """Detect and list active windows for selection."""
    windows = [win for win in gw.getAllWindows() if win.title and not win.isMinimized]
    common_apps = ["chrome", "firefox", "discord", "explorer", "spotify", "google", "mozilla"]
    filtered_windows = []
    for win in windows:
        title_lower = win.title.lower()
        if any(app in title_lower for app in common_apps):
            filtered_windows.append(win)
    return filtered_windows[:5]

def select_target_window():
    """Prompt user to select a target window and ensure focus."""
    windows = get_active_windows()
    if not windows:
        print("No suitable windows found. Ensure applications are open.")
        return None
    options = "\n".join(f"{i+1}. {win.title}" for i, win in enumerate(windows))
    choice = input(f"Select a window to type in:\n{options}\nEnter the number: ")
    try:
        index = int(choice) - 1
        if 0 <= index < len(windows):
            win = windows[index]
            try:
                win.activate()
            except gw.PyGetWindowException:
                print(f"Failed to activate window '{win.title}'. Clicking to focus instead.")
                x, y = win.left + win.width // 2, win.top + win.height // 2
                pyautogui.click(x, y)
                time.sleep(0.5)
            return win
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Enter a number.")
        return None

def calculate_delays(wpm, text):
    """Calculate base delay per character to achieve the target WPM."""
    total_chars = len(text)
    desired_time = (total_chars / 5) * (60 / wpm)  # Total time in seconds
    spaces = text.count(' ')
    newlines = text.count('\n')
    space_extra_avg = (SPACE_DELAY_RANGE[0] + SPACE_DELAY_RANGE[1]) / 2
    newline_avg = config["cooldown"]
    total_extra = (spaces * space_extra_avg) + (newlines * newline_avg)
    base_time = max(desired_time - total_extra, total_chars * 0.001)
    base_avg_time = base_time / total_chars
    return base_avg_time

def type_text(file_path, wpm, cooldown, error_prob):
    """Type text with human-like behavior using batch typing."""
    global typing_start_time, total_chars_typed, total_pause_time, pause_start_time
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            print("Text file is empty. Nothing to type.")
            return
        
        total_chars = len(text)
        base_avg_time = calculate_delays(wpm, text)
        typed_chars = 0
        typing_start_time = time.time()
        total_pause_time = 0
        
        for i in range(0, total_chars, BATCH_SIZE):
            if pause_event.is_set():
                pause_start_time = time.time()
                pause_event.wait()
                total_pause_time += time.time() - pause_start_time
            
            batch = text[i:i + BATCH_SIZE]
            batch_delay = base_avg_time * len(batch) * random.uniform(0.8, 1.2)
            
            if random.random() < (error_prob / 100) * len(batch):
                wrong_batch = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) 
                                    if random.random() < 0.2 else c for c in batch)
                pyautogui.typewrite(wrong_batch)
                time.sleep(ERROR_CORRECTION_DELAY)
                for _ in range(len(wrong_batch)):
                    pyautogui.press("backspace")
                time.sleep(POST_CORRECTION_DELAY)
            
            pyautogui.typewrite(batch, interval=base_avg_time / 2)
            typed_chars += len(batch)
            total_chars_typed = typed_chars
            
            if ' ' in batch:
                time.sleep(random.uniform(*SPACE_DELAY_RANGE))
            if '\n' in batch:
                time.sleep(cooldown)
            
            if total_chars > 0 and typed_chars % 50 == 0:
                percent = (typed_chars / total_chars) * 100
                print(f"Progress: {typed_chars}/{total_chars} characters ({percent:.1f}%)")
        
        elapsed_time = time.time() - typing_start_time
        active_time = elapsed_time - total_pause_time
        actual_wpm = (total_chars / 5) / (active_time / 60) if active_time > 0 else 0
        print(f"Target WPM: {wpm} | Actual WPM: {actual_wpm:.1f}")
        print(f"Typing completed in {elapsed_time:.1f} seconds (paused for {total_pause_time:.1f} seconds).")
        log_typing_session(file_path, total_chars, actual_wpm)
    
    except pyautogui.FailSafeException:
        print("Typing stopped: Mouse moved to corner (fail-safe triggered).")
    except Exception as e:
        print(f"Error during typing: {e}")

def on_pause_hotkey():
    """Toggle pause state with hotkey."""
    global pause_start_time
    if pause_event.is_set():
        pause_event.clear()
        print("Typing resumed.")
    else:
        pause_event.set()
        print("Typing paused. Press 'p' to resume.")

def configure(config):
    """Configure settings with input validation."""
    while True:
        print(f"\n--- Configuration ---\n1. Set WPM (current: {config['wpm']})\n2. Set Cooldown (current: {config['cooldown']} seconds)\n3. Set Error Probability (current: {config['error_prob']}%)\n4. Back to main menu")
        choice = input("Select an option (1-4): ").strip()
        if choice == "1":
            try:
                wpm = float(input("Enter your typing speed in WPM (60-220): "))
                if not 60 <= wpm <= 220:
                    raise ValueError("WPM must be between 60 and 220.")
                config["wpm"] = wpm
                save_config(config)
                print(f"WPM set to {wpm} and saved.")
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "2":
            try:
                cooldown = float(input("Enter cooldown after newline (0-10 seconds): "))
                if not 0 <= cooldown <= 10:
                    raise ValueError("Cooldown must be between 0 and 10 seconds.")
                config["cooldown"] = cooldown
                save_config(config)
                print(f"Cooldown set to {cooldown} seconds and saved.")
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "3":
            try:
                error_prob = float(input("Enter error probability (0-20%): "))
                if not 0 <= error_prob <= 20:
                    raise ValueError("Error probability must be between 0 and 20%.")
                config["error_prob"] = error_prob
                save_config(config)
                print(f"Error probability set to {error_prob}% and saved.")
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def main_menu():
    """Main menu loop."""
    global config
    config = load_config()
    listener = keyboard.GlobalHotKeys({'p': on_pause_hotkey})
    listener.start()
    
    try:
        while True:
            print(f"\n--- Human-like Typer v{VERSION} ---\n1. Configuration\n2. Typer\n3. Exit")
            choice = input("Select an option (1-3): ").strip()
            if choice == "1":
                configure(config)
                config = load_config()
            elif choice == "2":
                print("Ensure your keyboard layout matches the text's language.")
                text_path = get_text_file_path()
                target_window = select_target_window()
                if not target_window:
                    continue
                try:
                    with open(text_path, "r", encoding="utf-8") as f:
                        text = f.read()
                        if not text.strip():
                            print("Text file is empty. Nothing to type.")
                            continue
                    avg_time = calculate_delays(config["wpm"], text)
                    print(f"Target average time per character: {avg_time:.3f} seconds")
                    print("Starting in 3 seconds... Switch to your target window! Press 'p' to pause/resume.")
                    time.sleep(3)
                    pause_event.clear()
                    typing_thread = threading.Thread(target=type_text, args=(text_path, config["wpm"], config["cooldown"], config["error_prob"]))
                    typing_thread.start()
                    typing_thread.join()
                except Exception as e:
                    print(f"Error reading text file: {e}. Check the file and try again.")
            elif choice == "3":
                confirm = input("Are you sure you want to exit? (y/n): ").lower().strip()
                if confirm in ("y"):
                    print("Exiting program.")
                    break
            else:
                print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        listener.stop()

if __name__ == "__main__":
    print("Note: This script simulates keyboard input. Use responsibly and avoid misuse.")
    pyautogui.FAILSAFE = True
    main_menu()