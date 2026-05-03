import json
import logging
from copy import deepcopy

from hltyper.paths import CONFIG_PATH

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "wpm": 60,
    "cooldown": 3,
    "error_prob": 1.0,
    "language": "english",
    "hotkey_pause": "<f8>",
    "hotkey_stop": "<esc>",
    "mouse_edge_pause": True,
    "mouse_edge_pause_seconds": 2.5,
    "word_pause_min_ms": 20,
    "word_pause_max_ms": 120,
    "punctuation_extra_factor": 1.4,
    "thinking_pause_enabled": True,
    "thinking_pause_every_sentences": 4,
    "thinking_pause_min_ms": 150,
    "thinking_pause_max_ms": 600,
    "fatigue_enabled": False,
    "fatigue_after_chars": 800,
    "fatigue_slowdown_per_step": 0.02,
    "fatigue_max_slowdown": 1.25,
    "burst_enabled": False,
    "burst_probability": 0.08,
    "burst_chars": 12,
    "burst_speed_factor": 0.75,
    "window_list_limit": 25,
}


def merge_defaults(raw):
    out = deepcopy(DEFAULT_CONFIG)
    if not raw:
        return out
    for k, v in raw.items():
        out[k] = v
    return out


def load_config():
    import os

    if not os.path.exists(CONFIG_PATH):
        cfg = deepcopy(DEFAULT_CONFIG)
        save_config(cfg)
        return cfg
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return merge_defaults(raw)
    except Exception as e:
        logger.error("Error reading config: %s — using defaults.", e)
        return merge_defaults({})


def save_config(config):
    try:
        merged = merge_defaults(config)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=4)
    except Exception as e:
        logger.error("Error saving config: %s", e)


def config_dict_for_gui(cfg):
    """Return plain dict suitable for JSON (same keys as merged config)."""
    return merge_defaults(cfg)
