import pyautogui
import time
import random
import threading
import os
import sys
import json
import string
import pyperclip
from pynput import keyboard
from datetime import datetime

# Script metadata
VERSION = "1.3.0"  # Updated version

def get_script_directory():
    """Get the directory where the script or executable is running."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

script_dir = get_script_directory()
config_path = os.path.join(script_dir, "config.json")
log_path = os.path.join(script_dir, "typer_log.txt")

# Language translations with new entries
translations = {
    "en": {
        "menu": f"--- Human-like Typer v{VERSION} ---\n1. Configuration\n2. Typer\n3. Exit",
        "select_option": "Select an option (1-3): ",
        "config_menu": "--- Configuration ---\n1. Set WPM (current: {wpm})\n2. Set Language (current: {language})\n3. Set Cooldown (current: {cooldown} seconds)\n4. Set Error Probability (current: {error_prob}%)\n5. Back to main menu",
        "enter_wpm": "Enter your typing speed in WPM (60-220): ",
        "wpm_set": "WPM set to {wpm} and saved.",
        "enter_language": "Select language (en/sp/fr): ",
        "language_set": "Language set to {lang} and saved.",
        "enter_cooldown": "Enter cooldown after newline (0-10 seconds): ",
        "cooldown_set": "Cooldown set to {cooldown} seconds and saved.",
        "enter_error_prob": "Enter error probability (0-20%): ",
        "error_prob_set": "Error probability set to {error_prob}% and saved.",
        "ensure_keyboard": "Ensure your keyboard layout matches the text's language.",
        "enter_text_path": "Enter the path to the text file (or press Enter for 'text.txt'): ",
        "file_not_found": "File not found or inaccessible. Please try again.",
        "file_empty": "Text file is empty. Nothing to type.",
        "avg_time": "Target average time per character: {avg_time:.3f} seconds",
        "starting": "Starting in 3 seconds... Switch to your target window now! Press Ctrl+Alt+P to pause/resume.",
        "paused": "Typing paused. Press Ctrl+Alt+P to resume.",
        "resumed": "Typing resumed.",
        "typing_completed": "Typing completed in {elapsed:.1f} seconds.",
        "exiting": "Exiting program.",
        "config_error": "Error reading config file: {error}. Using defaults.",
        "confirm_exit": "Are you sure you want to exit? (y/n): ",
        "file_error": "Error reading text file: {error}. Check the file and try again.",
        "progress": "Progress: {typed}/{total} characters ({percent:.1f}%)",
        "typing_error": "Error during typing: {error}",
        "actual_wpm": "Actual WPM achieved: {wpm:.1f}",
        "log_entry": "Typed {chars} characters from {file} at {wpm:.1f} WPM on {date}"
    },
    "sp": {
        "menu": f"--- Escritor Humano v{VERSION} ---\n1. Configuración\n2. Escritor\n3. Salir",
        "select_option": "Seleccione una opción (1-3): ",
        "config_menu": "--- Configuración ---\n1. Establecer PPM (actual: {wpm})\n2. Establecer Idioma (actual: {language})\n3. Establecer Enfriamiento (actual: {cooldown} segundos)\n4. Establecer Probabilidad de Error (actual: {error_prob}%)\n5. Volver al menú principal",
        "enter_wpm": "Ingrese su velocidad de escritura en PPM (60-220): ",
        "wpm_set": "PPM establecido en {wpm} y guardado.",
        "enter_language": "Seleccione idioma (en/sp/fr): ",
        "language_set": "Idioma establecido en {lang} y guardado.",
        "enter_cooldown": "Ingrese el enfriamiento tras nueva línea (0-10 segundos): ",
        "cooldown_set": "Enfriamiento establecido en {cooldown} segundos y guardado.",
        "enter_error_prob": "Ingrese la probabilidad de error (0-20%): ",
        "error_prob_set": "Probabilidad de error establecida en {error_prob}% y guardada.",
        "ensure_keyboard": "Asegúrese de que su teclado esté configurado en el idioma del texto.",
        "enter_text_path": "Ingrese la ruta al archivo de texto (o presione Enter para 'text.txt'): ",
        "file_not_found": "Archivo no encontrado o inaccesible. Inténtelo de nuevo.",
        "file_empty": "El archivo de texto está vacío. Nada que escribir.",
        "avg_time": "Tiempo promedio objetivo por carácter: {avg_time:.3f} segundos",
        "starting": "Comenzando en 3 segundos... ¡Cambie a su ventana objetivo ahora! Presione Ctrl+Alt+P para pausar/reanudar.",
        "paused": "Escritura pausada. Presione Ctrl+Alt+P para reanudar.",
        "resumed": "Escritura reanudada.",
        "typing_completed": "Escritura completada en {elapsed:.1f} segundos.",
        "exiting": "Saliendo del programa.",
        "config_error": "Error al leer el archivo de configuración: {error}. Usando valores predeterminados.",
        "confirm_exit": "¿Está seguro de que desea salir? (s/n): ",
        "file_error": "Error al leer el archivo de texto: {error}. Verifique el archivo e intente de nuevo.",
        "progress": "Progreso: {typed}/{total} caracteres ({percent:.1f}%)",
        "typing_error": "Error durante la escritura: {error}",
        "actual_wpm": "PPM real alcanzado: {wpm:.1f}",
        "log_entry": "Escrito {chars} caracteres desde {file} a {wpm:.1f} PPM el {date}"
    },
    "fr": {
        "menu": f"--- Typer Humain v{VERSION} ---\n1. Configuration\n2. Typer\n3. Quitter",
        "select_option": "Sélectionnez une option (1-3): ",
        "config_menu": "--- Configuration ---\n1. Définir MPM (actuel: {wpm})\n2. Définir Langue (actuelle: {language})\n3. Définir Délai (actuel: {cooldown} secondes)\n4. Définir Probabilité d'Erreur (actuelle: {error_prob}%)\n5. Retour au menu principal",
        "enter_wpm": "Entrez votre vitesse de frappe en MPM (60-220): ",
        "wpm_set": "MPM défini à {wpm} et enregistré.",
        "enter_language": "Sélectionnez la langue (en/sp/fr): ",
        "language_set": "Langue définie à {lang} et enregistrée.",
        "enter_cooldown": "Entrez le délai après une nouvelle ligne (0-10 secondes): ",
        "cooldown_set": "Délai défini à {cooldown} secondes et enregistré.",
        "enter_error_prob": "Entrez la probabilité d'erreur (0-20%): ",
        "error_prob_set": "Probabilité d'erreur définie à {error_prob}% et enregistrée.",
        "ensure_keyboard": "Assurez-vous que votre clavier correspond à la langue du texte.",
        "enter_text_path": "Entrez le chemin du fichier texte (ou appuyez sur Entrée pour 'text.txt'): ",
        "file_not_found": "Fichier non trouvé ou inaccessible. Veuillez réessayer.",
        "file_empty": "Le fichier texte est vide. Rien à taper.",
        "avg_time": "Temps moyen cible par caractère: {avg_time:.3f} secondes",
        "starting": "Démarrage dans 3 secondes... Passez à votre fenêtre cible maintenant ! Appuyez sur Ctrl+Alt+P pour pause/reprise.",
        "paused": "Frappe en pause. Appuyez sur Ctrl+Alt+P pour reprendre.",
        "resumed": "Frappe reprise.",
        "typing_completed": "Frappe terminée en {elapsed:.1f} secondes.",
        "exiting": "Quitter le programme.",
        "config_error": "Erreur de lecture du fichier de configuration: {error}. Utilisation des valeurs par défaut.",
        "confirm_exit": "Êtes-vous sûr de vouloir quitter ? (o/n): ",
        "file_error": "Erreur de lecture du fichier texte: {error}. Vérifiez le fichier et réessayez.",
        "progress": "Progrès: {typed}/{total} caractères ({percent:.1f}%)",
        "typing_error": "Erreur pendant la frappe: {error}",
        "actual_wpm": "MPM réel atteint: {wpm:.1f}",
        "log_entry": "Tapé {chars} caractères depuis {file} à {wpm:.1f} MPM le {date}"
    }
}

# Constants
ERROR_CORRECTION_DELAY = 0.2
POST_CORRECTION_DELAY = 0.1
SPACE_DELAY_RANGE = (0.1, 0.3)

# Global variables
pause_event = threading.Event()
typing_start_time = 0
total_chars_typed = 0
config = {}

def load_config():
    """Load the config file or create a default one."""
    default_config = {"wpm": 60, "language": "en", "cooldown": 3, "error_prob": 1.0}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(translations["en"]["config_error"].format(error=str(e)))
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

def log_typing_session(file_path, chars, wpm, trans):
    """Log typing session to a file."""
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = trans["log_entry"].format(chars=chars, file=file_path, wpm=wpm, date=date)
            log_file.write(f"{entry}\n")
    except Exception as e:
        print(f"Error writing to log: {e}")

def get_text_file_path(trans):
    """Get and validate the text file path."""
    default_path = os.path.join(script_dir, "text.txt")
    while True:
        path = input(trans["enter_text_path"]).strip()
        if not path and os.path.exists(default_path):
            return default_path
        elif os.path.exists(path) and os.path.isfile(path):
            return path
        print(trans["file_not_found"])

def calculate_delays(wpm, text):
    """Calculate base delay per character to achieve the target WPM."""
    total_chars = len(text)
    spaces = text.count(' ')
    newlines = text.count('\n')
    desired_time = (total_chars / 5) * (60 / wpm)
    space_extra_avg = (SPACE_DELAY_RANGE[0] + SPACE_DELAY_RANGE[1]) / 2
    newline_avg = config["cooldown"]
    total_extra = (spaces * space_extra_avg) + (newlines * newline_avg)
    base_time = max(desired_time - total_extra, total_chars * 0.01)
    base_avg_time = base_time / total_chars
    return base_avg_time, space_extra_avg, newline_avg

def calculate_typing_delay(char, base_avg_time):
    """Calculate variable delay based on character type."""
    if char in string.punctuation:
        return random.uniform(base_avg_time * 0.8, base_avg_time * 1.8)
    elif char.isupper():
        return random.uniform(base_avg_time * 0.7, base_avg_time * 1.6)
    return random.uniform(base_avg_time * 0.5, base_avg_time * 1.5)

def type_character(char):
    """Type a single character using clipboard for UTF-8 support."""
    try:
        pyperclip.copy(char)
        if sys.platform == "darwin":  # macOS
            pyautogui.hotkey("command", "v")
        else:  # Windows/Linux
            pyautogui.hotkey("ctrl", "v")
    except Exception as e:
        print(f"Clipboard error: {e}")
        pyautogui.typewrite(char)  # Fallback

def type_text(file_path, wpm, cooldown, error_prob, trans):
    """Type text with human-like behavior."""
    global typing_start_time, total_chars_typed
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            print(trans["file_empty"])
            return
        
        total_chars = len(text)
        base_avg_time, _, _ = calculate_delays(wpm, text)
        typed_chars = 0
        typing_start_time = time.time()
        
        for char in text:
            if pause_event.is_set():
                pause_event.wait()
            
            if random.random() < (error_prob / 100):
                wrong_char = random.choice(string.ascii_letters + string.digits + string.punctuation)
                type_character(wrong_char)
                time.sleep(ERROR_CORRECTION_DELAY)
                pyautogui.press("backspace")
                time.sleep(POST_CORRECTION_DELAY)
            
            type_character(char)
            delay = calculate_typing_delay(char, base_avg_time)
            time.sleep(delay)
            typed_chars += 1
            total_chars_typed = typed_chars
            
            if char == ' ':
                time.sleep(random.uniform(*SPACE_DELAY_RANGE))
            elif char == '\n':
                time.sleep(cooldown)
            
            if total_chars > 0 and typed_chars % 50 == 0:
                percent = (typed_chars / total_chars) * 100
                print(trans["progress"].format(typed=typed_chars, total=total_chars, percent=percent))
        
        elapsed_time = time.time() - typing_start_time
        actual_wpm = (total_chars / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0
        print(trans["actual_wpm"].format(wpm=actual_wpm))
        print(trans["typing_completed"].format(elapsed=elapsed_time))
        log_typing_session(file_path, total_chars, actual_wpm, trans)
    
    except pyautogui.FailSafeException:
        print("Typing stopped: Mouse moved to corner (fail-safe triggered).")
    except Exception as e:
        print(trans["typing_error"].format(error=str(e)))

def on_pause_hotkey():
    """Toggle pause state with hotkey."""
    if pause_event.is_set():
        pause_event.clear()
        print(translations[config["language"]]["resumed"])
    else:
        pause_event.set()
        print(translations[config["language"]]["paused"])

def configure(config):
    """Configure settings with input validation."""
    trans = translations[config["language"]]
    while True:
        print("\n" + trans["config_menu"].format(wpm=config["wpm"], language=config["language"], 
                                                 cooldown=config["cooldown"], error_prob=config["error_prob"]))
        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            try:
                wpm = float(input(trans["enter_wpm"]))
                if not 60 <= wpm <= 220:
                    raise ValueError("WPM must be between 60 and 220.")
                config["wpm"] = wpm
                save_config(config)
                print(trans["wpm_set"].format(wpm=wpm))
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "2":
            lang = input(trans["enter_language"]).lower().strip()
            if lang in ["en", "sp", "fr"]:
                config["language"] = lang
                save_config(config)
                print(trans["language_set"].format(lang=lang))
            else:
                print("Invalid language. Choose en, sp, or fr.")
        elif choice == "3":
            try:
                cooldown = float(input(trans["enter_cooldown"]))
                if not 0 <= cooldown <= 10:
                    raise ValueError("Cooldown must be between 0 and 10 seconds.")
                config["cooldown"] = cooldown
                save_config(config)
                print(trans["cooldown_set"].format(cooldown=cooldown))
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "4":
            try:
                error_prob = float(input(trans["enter_error_prob"]))
                if not 0 <= error_prob <= 20:
                    raise ValueError("Error probability must be between 0 and 20%.")
                config["error_prob"] = error_prob
                save_config(config)
                print(trans["error_prob_set"].format(error_prob=error_prob))
            except ValueError as e:
                print(f"Invalid input: {e}")
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

def main_menu():
    """Main menu loop."""
    global config
    config = load_config()
    listener = keyboard.GlobalHotKeys({'<ctrl>+<alt>+p': on_pause_hotkey})
    listener.start()
    
    try:
        while True:
            trans = translations[config["language"]]
            print("\n" + trans["menu"])
            choice = input(trans["select_option"]).strip()
            if choice == "1":
                configure(config)
                config = load_config()
            elif choice == "2":
                print(trans["ensure_keyboard"])
                text_path = get_text_file_path(trans)
                try:
                    with open(text_path, "r", encoding="utf-8") as f:
                        text = f.read()
                        if not text.strip():
                            print(trans["file_empty"])
                            continue
                    avg_time, _, _ = calculate_delays(config["wpm"], text)
                    print(trans["avg_time"].format(avg_time=avg_time))
                    print(trans["starting"])
                    time.sleep(3)
                    pause_event.clear()
                    typing_thread = threading.Thread(target=type_text, args=(text_path, config["wpm"], config["cooldown"], config["error_prob"], trans))
                    typing_thread.start()
                    typing_thread.join()
                except Exception as e:
                    print(trans["file_error"].format(error=str(e)))
            elif choice == "3":
                confirm = input(trans["confirm_exit"]).lower().strip()
                if confirm in ("y", "s", "o"):
                    print(trans["exiting"])
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