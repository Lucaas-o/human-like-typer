import logging
import random
import string
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime

import pyautogui

from hltyper.paths import LOG_PATH, SESSION_LOG_PATH

logger = logging.getLogger(__name__)

ERROR_CORRECTION_DELAY = 0.1
POST_CORRECTION_DELAY = 0.05
BATCH_SIZE = 5

QWERTY_ADJACENT = {
    "a": "qsxz",
    "b": "vghn",
    "c": "xdfv",
    "d": "serfc",
    "e": "w34rd",
    "f": "drtgc",
    "g": "ftyhb",
    "h": "gyujb",
    "i": "u89ok",
    "j": "huikn",
    "n": "bhjm",
    "o": "i90pl",
    "p": "o0l[",
    "q": "12wa",
    "r": "e45tf",
    "s": "awedx",
    "t": "r56yg",
    "u": "y78ij",
    "v": "cfgb",
    "w": "q23es",
    "x": "zsdc",
    "y": "t67uh",
    "z": "asx",
}
SPANISH_ADJACENT = {
    **QWERTY_ADJACENT,
    "n": "bhjmñ",
    "ñ": "nm",
    "o": "i90pló",
    "á": "aqs",
    "é": "ew3",
    "í": "iu8",
    "ó": "op9",
    "ú": "uy7",
}

PUNCT_EXTRA = set(".,;:!?)]}'\"\"«»…")

ASCII_FALLBACK_TYPOS = string.ascii_letters + string.digits


def calculate_delays(wpm: float, text: str) -> float:
    total_chars = max(len(text), 1)
    desired_time = (total_chars / 5) * (60 / max(wpm, 1))
    return desired_time / total_chars


def _layout_for_language(language: str):
    return SPANISH_ADJACENT if language == "spanish" else QWERTY_ADJACENT


def _can_receive_typo(char: str) -> bool:
    if char.isspace() or len(char) != 1:
        return False
    cat = unicodedata.category(char)
    return cat.startswith("L") or cat == "Nd"


def get_typo(char: str, layout: dict) -> str:
    char_lower = char.lower()
    if char_lower in layout:
        return random.choice(layout[char_lower])
    if char.isascii() and char.isalnum():
        return random.choice(ASCII_FALLBACK_TYPOS)
    return char


def check_mouse_pause():
    screen_width, screen_height = pyautogui.size()
    mouse_x, mouse_y = pyautogui.position()
    return (mouse_x <= 0 or mouse_x >= screen_width - 1) and not (
        mouse_y <= 0 or mouse_y >= screen_height - 1
    )


def _fatigue_multiplier(typed_chars: int, cfg: dict) -> float:
    if not cfg.get("fatigue_enabled"):
        return 1.0
    step = max(1, int(cfg.get("fatigue_after_chars", 800)))
    steps = typed_chars // step
    per = float(cfg.get("fatigue_slowdown_per_step", 0.02))
    cap = float(cfg.get("fatigue_max_slowdown", 1.25))
    return min(cap, 1.0 + steps * per)


def _append_session_log(line: str):
    try:
        with open(SESSION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        logger.error("Session log write failed: %s", e)


def log_typing_session_line(file_path: str, chars: int, wpm: float):
    try:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"Typed {chars} characters from {file_path} at {wpm:.1f} WPM on {date}"
        with open(LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(entry + "\n")
    except Exception as e:
        logger.error("typer_log.txt write failed: %s", e)


@dataclass
class TypingResult:
    ok: bool = True
    stopped_by_user: bool = False
    chars_typed: int = 0
    elapsed_seconds: float = 0.0
    pause_seconds: float = 0.0
    actual_wpm: float = 0.0
    message: str = ""


def _sleep_mouse_pause(cfg, total_pause_time_ref: list) -> None:
    """Pause if mouse at edge; updates total_pause_time_ref[0]."""
    if not cfg.get("mouse_edge_pause", True):
        return
    if not check_mouse_pause():
        return
    sec = float(cfg.get("mouse_edge_pause_seconds", 2.5))
    logger.info("Mouse edge pause %.1fs", sec)
    print(f"Typing paused (mouse at screen edge). Resuming in {sec:.1f}s…")
    t0 = time.time()
    time.sleep(sec)
    total_pause_time_ref[0] += time.time() - t0
    print("Typing resumed.")


def run_typing(
    text: str,
    source_label: str,
    cfg: dict,
    *,
    dry_run: bool = False,
    progress_callback=None,
    hotkey_controller=None,
) -> TypingResult:
    result = TypingResult()
    if not text.strip():
        result.ok = False
        result.message = "Nothing to type (empty text)."
        logger.warning(result.message)
        return result

    layout = _layout_for_language(cfg.get("language", "english"))
    total_chars = len(text)
    base_avg_time = calculate_delays(float(cfg.get("wpm", 60)), text)
    typed_chars = 0
    typing_start = time.time()
    total_pause = [0.0]
    sentence_counter = 0
    burst_rem = [0]

    def wait_paused():
        while hotkey_controller and hotkey_controller.paused:
            if hotkey_controller.stop_requested.is_set():
                return True
            time.sleep(0.05)
        return False

    def stopped():
        return hotkey_controller and hotkey_controller.stop_requested.is_set()

    def sleep_ms(low_ms, high_ms):
        time.sleep(random.uniform(low_ms, high_ms) / 1000.0)

    def wrong_char_delay():
        ft = _fatigue_multiplier(typed_chars, cfg)
        return base_avg_time * random.uniform(0.8, 1.2) * ft

    def char_delay(char: str, typed_so_far: int):
        ft = _fatigue_multiplier(typed_so_far, cfg)
        jitter = random.uniform(0.8, 1.2)
        burst_mul = float(cfg.get("burst_speed_factor", 0.75)) if burst_rem[0] > 0 else 1.0
        if burst_rem[0] > 0:
            burst_rem[0] -= 1
        delay = base_avg_time * jitter * ft * burst_mul
        if char in PUNCT_EXTRA:
            delay *= float(cfg.get("punctuation_extra_factor", 1.4))
        return delay

    try:
        for batch_start in range(0, total_chars, BATCH_SIZE):
            if stopped():
                result.stopped_by_user = True
                break
            if wait_paused():
                result.stopped_by_user = True
                break

            batch = text[batch_start : batch_start + BATCH_SIZE]
            prob = (float(cfg.get("error_prob", 0)) / 100.0) * len(batch)
            batch_has_error = random.random() < prob

            if batch_has_error:

                def typo_char(c):
                    if not _can_receive_typo(c):
                        return c
                    if random.random() >= 0.22:
                        return c
                    return get_typo(c, layout)

                wrong_batch = "".join(typo_char(c) for c in batch)

                for char in wrong_batch:
                    if stopped() or wait_paused():
                        result.stopped_by_user = True
                        break
                    _sleep_mouse_pause(cfg, total_pause)
                    if result.stopped_by_user:
                        break
                    if not dry_run:
                        pyautogui.typewrite(char)
                    time.sleep(wrong_char_delay())
                if result.stopped_by_user:
                    break

                time.sleep(ERROR_CORRECTION_DELAY)
                for _ in wrong_batch:
                    if stopped() or wait_paused():
                        result.stopped_by_user = True
                        break
                    if not dry_run:
                        pyautogui.press("backspace")
                if result.stopped_by_user:
                    break
                time.sleep(POST_CORRECTION_DELAY)

            for j, char in enumerate(batch):
                if stopped() or wait_paused():
                    result.stopped_by_user = True
                    break

                idx = batch_start + j
                _sleep_mouse_pause(cfg, total_pause)

                if cfg.get("burst_enabled") and burst_rem[0] == 0:
                    if random.random() < float(cfg.get("burst_probability", 0.08)):
                        burst_rem[0] = int(cfg.get("burst_chars", 12))

                delay = char_delay(char, typed_chars)

                if not dry_run:
                    pyautogui.typewrite(char)
                time.sleep(delay)

                typed_chars += 1

                if char == " ":
                    sleep_ms(
                        float(cfg.get("word_pause_min_ms", 20)),
                        float(cfg.get("word_pause_max_ms", 120)),
                    )
                elif char == "\n":
                    time.sleep(float(cfg.get("cooldown", 3)))

                next_ch = text[idx + 1] if idx + 1 < total_chars else ""
                if char in ".!?" and (not next_ch or next_ch in " \n\r\t"):
                    sentence_counter += 1
                    n = int(cfg.get("thinking_pause_every_sentences", 4))
                    if (
                        cfg.get("thinking_pause_enabled")
                        and n > 0
                        and sentence_counter % n == 0
                    ):
                        sleep_ms(
                            float(cfg.get("thinking_pause_min_ms", 150)),
                            float(cfg.get("thinking_pause_max_ms", 600)),
                        )

                if progress_callback and total_chars > 0 and typed_chars % 50 == 0:
                    progress_callback(typed_chars, total_chars)

            if result.stopped_by_user:
                break

        elapsed = time.time() - typing_start
        active_time = elapsed - total_pause[0]
        actual_wpm = (
            (typed_chars / 5) / (active_time / 60) if active_time > 0 else 0
        )

        result.chars_typed = typed_chars
        result.elapsed_seconds = elapsed
        result.pause_seconds = total_pause[0]
        result.actual_wpm = actual_wpm

        status = "stopped early" if result.stopped_by_user else "completed"
        summary = (
            f"session {status}: source={source_label} chars={typed_chars}/{total_chars} "
            f"target_wpm={cfg.get('wpm')} actual_wpm={actual_wpm:.1f} "
            f"elapsed={elapsed:.1f}s paused={total_pause[0]:.1f}s dry_run={dry_run}"
        )
        logger.info(summary)
        _append_session_log(summary)

        if not dry_run and typed_chars > 0:
            log_typing_session_line(source_label, typed_chars, actual_wpm)

        print(
            f"Target WPM: {cfg.get('wpm')} | Actual WPM: {actual_wpm:.1f}\n"
            f"Typing {status} in {elapsed:.1f}s (paused {total_pause[0]:.1f}s)."
        )

    except pyautogui.FailSafeException:
        logger.warning("Fail-safe triggered.")
        print("Typing stopped: mouse moved to corner (PyAutoGUI fail-safe).")
        result.ok = False
        result.message = "Fail-safe"
    except Exception as e:
        logger.exception("Typing error")
        result.ok = False
        result.message = str(e)
        print(f"Error during typing: {e}")

    return result
