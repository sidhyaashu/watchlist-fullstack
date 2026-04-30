import logging
import sys
from typing import Any


def setup_logger(name: str = "watchlist_service") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 🔹 Console Handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # 🔹 Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger


logger = setup_logger()
