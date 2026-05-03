import logging
import os
import time

from hltyper.config import merge_defaults
from hltyper.engine import TypingResult, calculate_delays, run_typing
from hltyper.hotkeys import TypingHotkeyController
from hltyper.windowing import activate_window, list_candidate_windows, select_target_window_interactive

logger = logging.getLogger(__name__)


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_typing_session(
    *,
    file_path: str | None = None,
    text: str | None = None,
    source_label: str = "clipboard",
    cfg: dict | None = None,
    dry_run: bool = False,
    foreground_only: bool = False,
    pick_window: bool = True,
    countdown: float = 3.0,
    progress_callback=None,
    pre_selected_window=None,
) -> TypingResult:
    """
    Full session: optional window targeting, hotkeys, typing.

    `pre_selected_window`: pygetwindow window object from GUI (skip interactive picker).
    """
    cfg = merge_defaults(cfg or {})
    result = TypingResult()

    if file_path:
        if not os.path.isfile(file_path):
            result.ok = False
            result.message = f"Not a file: {file_path}"
            return result
        try:
            text = load_text_file(file_path)
        except Exception as e:
            result.ok = False
            result.message = str(e)
            return result
        source_label = file_path

    if text is None:
        result.ok = False
        result.message = "No text provided."
        return result

    if not text.strip():
        result.ok = False
        result.message = "Text is empty."
        return result

    limit = int(cfg.get("window_list_limit", 25))

    if pick_window and not foreground_only and not dry_run:
        if pre_selected_window is not None:
            activate_window(pre_selected_window)
        else:
            win = select_target_window_interactive(limit=limit)
            if win is None:
                result.ok = False
                result.message = "No target window selected."
                return result

    avg = calculate_delays(float(cfg.get("wpm", 60)), text)
    logger.info(
        "Starting session dry_run=%s foreground_only=%s avg_delay=%.4fs chars=%s",
        dry_run,
        foreground_only,
        avg,
        len(text),
    )
    print(f"Target average time per character: {avg:.4f}s")
    hp = cfg.get("hotkey_pause", "<f8>")
    hs = cfg.get("hotkey_stop", "<esc>")
    print(
        f"Starting in {countdown:.0f}s… Hotkeys: pause {hp}, stop {hs}. "
        "Mouse at left/right screen edge pauses; corner triggers fail-safe stop."
    )
    if countdown > 0:
        time.sleep(float(countdown))

    ctrl = TypingHotkeyController(cfg.get("hotkey_pause"), cfg.get("hotkey_stop"))
    with ctrl:
        result = run_typing(
            text,
            source_label,
            cfg,
            dry_run=dry_run,
            progress_callback=progress_callback,
            hotkey_controller=ctrl,
        )
    return result


def list_windows_for_gui(filter_substring: str, cfg: dict):
    cfg = merge_defaults(cfg or {})
    return list_candidate_windows(
        filter_substring,
        limit=int(cfg.get("window_list_limit", 25)),
    )


def dry_run_estimate(cfg: dict, text: str) -> dict:
    """Summarize timing without sending keys."""
    cfg = merge_defaults(cfg or {})
    avg = calculate_delays(float(cfg.get("wpm", 60)), text)
    total = len(text)
    est_sec = avg * total * 1.05
    return {
        "chars": total,
        "avg_delay_per_char": avg,
        "approx_seconds": est_sec,
        "target_wpm": cfg.get("wpm"),
    }
