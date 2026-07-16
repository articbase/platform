from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DEFAULT_LOG_FILE = "logs/app.log"


def configure_application_logging() -> logging.Logger:
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_file = Path(os.getenv("APP_LOG_FILE", DEFAULT_LOG_FILE))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    resolved_log_file = str(log_file.resolve())

    existing_file_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(handler, RotatingFileHandler) and handler.baseFilename == resolved_log_file
        ),
        None,
    )
    if existing_file_handler is None:
        file_handler = RotatingFileHandler(resolved_log_file, maxBytes=1_000_000, backupCount=3)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    if not any(isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

    return logger
