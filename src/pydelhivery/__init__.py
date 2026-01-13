from pydelhivery.utils.logger import setup_logging


setup_logging()

# Expose the logger for easy access
import logging

logger = logging.getLogger("pydelhivery")
