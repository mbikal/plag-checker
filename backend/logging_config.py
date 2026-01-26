"""Logging configuration for the backend."""
from __future__ import annotations

import logging

from backend import config


def get_logger() -> logging.Logger:
    """Return a configured logger for the app."""
    logger = logging.getLogger("plag_checker")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(config.LOG_FILE)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
    return logger
