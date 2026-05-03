import logging
from logging.handlers import RotatingFileHandler
import os

from hltyper.paths import SESSION_LOG_PATH


def setup_logging(level=logging.INFO):
    root = logging.getLogger()
    if root.handlers:
        return root
    root.setLevel(level)
    os.makedirs(os.path.dirname(SESSION_LOG_PATH) or ".", exist_ok=True)
    fh = RotatingFileHandler(
        SESSION_LOG_PATH,
        maxBytes=512_000,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s")
    )
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(fh)
    root.addHandler(sh)
    return root
