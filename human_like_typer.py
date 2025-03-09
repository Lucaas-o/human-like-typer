import pyautogui
import time
import random
import threading
import os
import sys
import json

# Script metadata
VERSION = "1.0.0"

def get_script_directory():
    """Get the directory where the script or executable is running."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

script_dir = get_script_directory()
config_path = os.path.join(script_dir, "config.txt")

# Language translations
translations = {
    "en": {
        "menu": f"--- Human-like Typer v{VERSION} ---\n1. Configuration\n2. Typer\n3. Exit",
        "select_option": "Select an option (1-3): ",
        "config_menu": "--- Configuration ---\n1. Set WPM (current: {wpm})\n2. Set Language (current: {language})\n3. Set Cooldown (current: {cooldown} seconds)\n4. Back to main menu",
        "enter_wpm": "Enter your typing speed in WPM: ",
        "wpm_set": "WPM set to {wpm} and saved.",
        "enter_language": "Select language (en/sp/fr): ",
        "language_set": "Language set to {lang} and saved.",
        "enter_cooldown": "Enter cooldown after newline (seconds): ",
        "cooldown_set": "Cooldown set to {cooldown} seconds and saved.",
        "ensure_keyboard": "Ensure your keyboard layout matches the text's language.",
        "enter_text_path": "Enter the path to the text file (or press Enter for 'text.txt'): ",
        "file_not_found": "File not found. Please try again.",
        "avg_time": "Average time per character: {avg_time:.2f} seconds",
        "starting": "Starting in 3 seconds... Switch to your target window now!",
        "press_enter": "Press Enter to pause/resume...",
        "paused_after_newline": "Paused after newline, resuming in {cooldown} seconds...",
        "typing_resumed": "Typing resumed.",
        "typing_paused": "Typing paused.",
        "typing_completed": "Typing completed.",
        "exiting": "Exiting program.",
        "config_error": "Error reading config file. Using defaults.",
        "confirm_exit": "Are you sure you want to exit? (y/n): ",
        "file_error": "Error reading text file. Check the file and try again."
    },
    "sp": {
        "menu": f"--- Escritor Humano v{VERSION} ---\n1. Configuración\n2. Escritor\n3. Salir",
        "select_option": "Seleccione una opción (1-3): ",
        "config_menu": "--- Configuración ---\n1. Establecer PPM (actual: {wpm})\n2. Establecer Idioma (actual: {language})\n3. Establecer Tiempo de Espera (actual: {cooldown} segundos)\n4. Volver al menú principal",
        "enter_wpm": "Ingrese su velocidad de escritura en PPM: ",
        "wpm_set": "PPM establecido en {wpm} y guardado.",
        "enter_language": "Seleccione el idioma (en/sp/fr): ",
        "language_set": "Idioma establecido en {lang} y guardado.",
        "enter_cooldown": "Ingrese el tiempo de espera tras nueva línea (segundos): ",
        "cooldown_set": "Tiempo de espera establecido en {cooldown} segundos y guardado.",
        "ensure_keyboard": "Asegúrese de que su teclado esté configurado en el idioma del texto.",
        "enter_text_path": "Ingrese la ruta del archivo de texto (o presione Enter para 'text.txt'): ",
        "file_not_found": "Archivo no encontrado. Inténtelo de nuevo.",
        "avg_time": "Tiempo promedio por carácter: {avg_time:.2f} segundos",
        "starting": "Comenzando en 3 segundos... Cambie a su ventana objetivo ahora!",
        "press_enter": "Presione Enter para pausar/reanudar...",
        "paused_after_newline": "Pausado tras nueva línea, reanudando en {cooldown} segundos...",
        "typing_resumed": "Escritura reanudada.",
        "typing_paused": "Escritura pausada.",
        "typing_completed": "Escritura completada.",
        "exiting": "Saliendo del programa.",
        "config_error": "Error al leer el archivo de configuración. Usando valores predeterminados.",
        "confirm_exit": "¿Está seguro de que desea salir? (s/n): ",
        "file_error": "Error al leer el archivo de texto. Verifique el archivo e intente de nuevo."
    },
    "fr": {
        "menu": f"--- Typer Humain v{VERSION} ---\n1. Configuration\n2. Typer\n3. Quitter",
        "select_option": "Sélectionnez une option (1-3): ",
        "config_menu": "--- Configuration ---\n1. Définir MPM (actuel: {wpm})\n2. Définir Langue (actuelle: {language})\n3. Définir Délai (actuel: {cooldown} secondes)\n4. Retour au menu principal",
        "enter_wpm": "Entrez votre vitesse de frappe en MPM: ",
        "wpm_set": "MPM défini à {wpm} et enregistré.",
        "enter_language": "Sélectionnez la langue (en/sp/fr): ",
        "language_set": "Langue définie à {lang} et enregistrée.",
        "enter_cooldown": "Entrez le délai après une nouvelle ligne (secondes): ",
        "cooldown_set": "Délai défini à {cooldown} secondes et enregistré.",
        "ensure_keyboard": "Assurez-vous que votre clavier est configuré dans la langue du texte.",
        "enter_text_path": "Entrez le chemin du fichier texte (ou appuyez sur Entrée pour 'text.txt'): ",
        "file_not_found": "Fichier non trouvé. Veuillez réessayer.",
        "avg_time": "Temps moyen par caractère: {avg_time:.2f} secondes",
        "starting": "Démarrage dans 3 secondes... Basculez vers votre fenêtre cible maintenant!",
        "press_enter": "Appuyez sur Entrée pour mettre en pause/reprendre...",
        "paused_after_newline": "Pause après nouvelle ligne, reprise dans {cooldown} secondes...",
        "typing_resumed": "Frappe reprise.",
        "typing_paused": "Frappe en pause.",
        "typing_completed": "Frappe terminée.",
        "exiting": "Quitter le programme.",
        "config_error": "Erreur lors de la lecture du fichier de configuration. Utilisation des valeurs par défaut.",
        "confirm_exit": "Êtes-vous sûr de vouloir quitter ? (o/n): ",
        "file_error": "Erreur lors de la lecture du fichier texte. Vérifiez le fichier et réessayez."
    }
}

# Global pause flag
pause_flag = False

def load_config():
    """Load the config file if it exists, otherwise create a default one."""
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(translations["en"]["config_error"])
    # Default config with all settings
    config = {"wpm": 60, "language": "en", "cooldown": 3}
    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)
    return config

def save_config(config):
    """Save configuration to config.txt in the script's directory using JSON format."""
    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)

def get_text_file_path(trans):
    """Get the text file path, defaulting to 'text.txt' if available."""
    default_path = os.path.join(script_dir, "text.txt")
    while True:
        path = input(trans["enter_text_path"])
        if path == "" and os.path.exists(default_path):
            return default_path
        elif os.path.exists(path):
            return path
        else:
            print(trans["file_not_found"])

def type_text(text, avg_time, cooldown, trans):
    """Type text with human-like delays and automatic cooldowns."""
    global pause_flag
    for char in text:
        while pause_flag:
            time.sleep(0.1)
        pyautogui.typewrite(char)
        delay = random.uniform(avg_time * 0.5, avg_time * 1.5)
        time.sleep(delay)
        if char == '\n':
            print(trans["paused_after_newline"].format(cooldown=cooldown))
            time.sleep(cooldown)
            print(trans["typing_resumed"])
        elif char == ' ':
            time.sleep(random.uniform(0.1, 0.3))

def pause_resume(trans):
    """Toggle pause state and display status."""
    global pause_flag
    pause_flag = not pause_flag
    status = "paused" if pause_flag else "resumed"
    print(trans[f"typing_{status}"])

def configure(config):
    """Configure WPM, language, and cooldown settings."""
    trans = translations[config["language"]]
    while True:
        print("\n" + trans["config_menu"].format(wpm=config["wpm"], language=config["language"], cooldown=config["cooldown"]))
        choice = input("Select an option (1-4): ")
        if choice == "1":
            try:
                wpm = float(input(trans["enter_wpm"]))
                config["wpm"] = wpm
                save_config(config)
                print(trans["wpm_set"].format(wpm=wpm))
            except ValueError:
                print("Invalid input for WPM.")
        elif choice == "2":
            lang = input(trans["enter_language"])
            if lang in ["en", "sp", "fr"]:
                config["language"] = lang
                save_config(config)
                print(trans["language_set"].format(lang=lang))
            else:
                print("Invalid language. Choose en, sp, or fr.")
        elif choice == "3":
            try:
                cooldown = int(input(trans["enter_cooldown"]))
                config["cooldown"] = cooldown
                save_config(config)
                print(trans["cooldown_set"].format(cooldown=cooldown))
            except ValueError:
                print("Invalid input for cooldown.")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def calculate_avg_time(wpm):
    """Calculate the average time per character based on words per minute."""
    return 60 / (wpm * 5)

def main_menu():
    """Main menu loop."""
    config = load_config()
    while True:
        trans = translations[config["language"]]
        print("\n" + trans["menu"])
        choice = input(trans["select_option"])
        if choice == "1":
            configure(config)
            config = load_config()  # Reload config in case of changes
        elif choice == "2":
            print(trans["ensure_keyboard"])
            text_path = get_text_file_path(trans)
            try:
                with open(text_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                print(trans["file_error"])
                continue
            avg_time = calculate_avg_time(config["wpm"])
            print(trans["avg_time"].format(avg_time=avg_time))
            print(trans["starting"])
            time.sleep(3)
            typing_thread = threading.Thread(target=type_text, args=(text, avg_time, config["cooldown"], trans))
            typing_thread.start()
            while typing_thread.is_alive():
                input(trans["press_enter"])
                pause_resume(trans)
            print(trans["typing_completed"])
        elif choice == "3":
            confirm = input(trans["confirm_exit"])
            if confirm.lower() in ("y", "s", "o"):  # Yes in en/sp/fr
                print(trans["exiting"])
                break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
