"""Settings and configuration for the poster generator library."""

import logging
from pathlib import Path

LIBRARY_NAME = "Poster Generator"
LIBRARY_SLUG = "poster-generator"

DEBUG = True

def get_logger():
    """
    Get the library's logger instance.
    
    Returns:
        logging.Logger: Configured logger for the poster generator library.
    """
    return logging.getLogger(LIBRARY_SLUG)

logger = get_logger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
logger.addHandler(logging.StreamHandler())

DEFAULT_FONT = Path(__file__).parent / "resources/fonts/open_sans.ttf"
