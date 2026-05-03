import os
import sys


def get_project_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # hltyper/paths.py -> project root is parent of hltyper/
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


_ROOT = get_project_root()
CONFIG_PATH = os.path.join(_ROOT, "config.json")
LOG_PATH = os.path.join(_ROOT, "typer_log.txt")
SESSION_LOG_PATH = os.path.join(_ROOT, "typer_session.log")
