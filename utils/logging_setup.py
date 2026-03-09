"""
utils/logging_setup.py
Configures logging for the entire trading bot.
Logs to both console and logs/trading.log.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config.settings import LOG_FILE, LOG_LEVEL


def setup_logging() -> None:
    """
    Initialize root logger with:
    - Console handler (INFO level)
    - Rotating file handler → logs/trading.log (all levels)
    
    Call once at application startup.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(fmt)

    # Rotating file handler (max 5MB × 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    if not root.handlers:
        root.addHandler(console)
        root.addHandler(file_handler)
