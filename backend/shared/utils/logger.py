"""
General utility functions for logging and common operations.
"""

import sys
import logging


def get_logger(name: str):
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    logger.propagate = False

    return logger
