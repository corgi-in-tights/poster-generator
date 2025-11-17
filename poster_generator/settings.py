import logging
from pathlib import Path

LIBRARY_NAME = "Poster Generator"
LIBRARY_SLUG = "poster-generator"

def get_logger():
    return logging.getLogger(LIBRARY_SLUG)

logger = get_logger()
logger.setLevel(logging.INFO)

DEFAULT_FONT = Path(__file__).parent / "fonts" / "open_sans.ttf"
