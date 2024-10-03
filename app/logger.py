# Path: app/logging.py
# Description: Logging configuration for the application.

# from functools import lru_cache
import logging
import logging.config

# @lru_cache
def get_logger():
    """Get a logger instance."""
    logging.config.fileConfig("logging.conf")
    # logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    return logger
