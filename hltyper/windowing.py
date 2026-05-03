import logging
import time

import pyautogui
import pygetwindow as gw

logger = logging.getLogger(__name__)


def list_candidate_windows(filter_substring="", limit=25):
    """Return visible windows with titles, optionally filtered by substring (case-insensitive)."""
    try:
        all_wins = gw.getAllWindows()
    except Exception as e:
        logger.error("Could not enumerate windows: %s", e)
        return []

    needle = (filter_substring or "").strip().lower()
    out = []
    for win in all_wins:
        if not win.title or not win.title.strip():
            continue
        if win.isMinimized:
            continue
        title_lower = win.title.lower()
        if needle and needle not in title_lower:
            continue
        out.append(win)

    # Stable sort: shorter titles first often reads nicer; then alpha
    out.sort(key=lambda w: (len(w.title), w.title.lower()))
    return out[: max(1, min(limit, 100))]


def activate_window(win):
    try:
        win.activate()
        time.sleep(0.15)
        return True
    except gw.PyGetWindowException:
        logger.warning("activate() failed for '%s' — clicking center.", win.title)
        try:
            x = win.left + max(1, win.width) // 2
            y = win.top + max(1, win.height) // 2
            pyautogui.click(x, y)
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error("Click focus failed: %s", e)
            return False


def select_target_window_interactive(limit=25):
    """CLI: optional filter string then numbered pick."""
    filt = input("Filter window titles (Enter for all): ").strip()
    windows = list_candidate_windows(filt, limit=limit)
    if not windows:
        print("No windows matched. Open an application or adjust the filter.")
        return None
    options = "\n".join(f"{i+1}. {win.title}" for i, win in enumerate(windows))
    choice = input(f"Select window to type in:\n{options}\nEnter number (or 0 to cancel): ").strip()
    try:
        index = int(choice) - 1
        if index == -1:
            return None
        if 0 <= index < len(windows):
            win = windows[index]
            activate_window(win)
            return win
    except ValueError:
        pass
    print("Invalid selection.")
    return None
