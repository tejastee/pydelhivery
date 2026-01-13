# src/pydelhivery/utils/logger.py
import logging
import os
from rich.logging import RichHandler


def setup_logging():
    """Initializes logging based on the PYDELHIVERY_LOGGING env var."""

    # Grab level from env, default to INFO if not set or invalid
    log_level = os.getenv("PYDELHIVERY_LOGGING", "DEBUG").upper()

    # Map string to logging constants (handles typos gracefully)
    numeric_level = getattr(logging, log_level, logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )

    return logging.getLogger("pydelhivery")
