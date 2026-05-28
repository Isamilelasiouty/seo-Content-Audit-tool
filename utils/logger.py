"""
utils/logger.py
───────────────
Centralised logging setup.
Every module imports `get_logger(__name__)` – no print() statements.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config.settings import LOG_DIR


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a logger that writes to both console and a rotating log file.

    Parameters
    ----------
    name  : Module name, typically __name__
    level : Logging level (default INFO)
    """
    logger = logging.getLogger(name)
    if logger.handlers:          # already configured in this process
        return logger

    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ──────────────────────────────────────────────────────
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # ── File handler (rotates at 10 MB, keeps 5 backups) ─────────────────────
    log_file = LOG_DIR / "seo_tool.log"
    fh = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5,
                              encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
