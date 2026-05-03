import logging
import threading

from pynput import keyboard

logger = logging.getLogger(__name__)


def normalize_hotkey_spec(spec):
    """Ensure pynput GlobalHotKeys format (e.g. f8 -> <f8>, esc -> <esc>)."""
    s = (spec or "").strip().lower()
    if not s:
        return "<f8>"
    if s.startswith("<") and s.endswith(">"):
        return s
    if len(s) == 1 and s.isalpha():
        return s
    return f"<{s}>"


class TypingHotkeyController:
    """Toggle pause and signal stop via global hotkeys while typing runs."""

    def __init__(self, pause_spec: str, stop_spec: str):
        self._pause_combo = normalize_hotkey_spec(pause_spec)
        self._stop_combo = normalize_hotkey_spec(stop_spec)
        if self._pause_combo == self._stop_combo:
            logger.warning(
                "Pause and stop hotkeys are identical (%s); stop action wins.",
                self._stop_combo,
            )
        self.paused = False
        self.stop_requested = threading.Event()
        self._hk = None
        self._lock = threading.Lock()

    def _toggle_pause(self):
        with self._lock:
            self.paused = not self.paused
        state = "paused" if self.paused else "resumed"
        logger.info("Hotkey: typing %s.", state)
        print(f"Typing {state} ({self._pause_combo}).")

    def _stop(self):
        self.stop_requested.set()
        logger.info("Hotkey: stop requested.")
        print("Stop requested — finishing after current key…")

    def __enter__(self):
        if self._pause_combo == self._stop_combo:
            mapping = {self._stop_combo: self._stop}
        else:
            mapping = {
                self._pause_combo: self._toggle_pause,
                self._stop_combo: self._stop,
            }
        self._hk = keyboard.GlobalHotKeys(mapping)
        self._hk.start()
        return self

    def __exit__(self, *args):
        if self._hk:
            try:
                self._hk.stop()
            except Exception as e:
                logger.debug("Hotkey stop: %s", e)
            self._hk = None
