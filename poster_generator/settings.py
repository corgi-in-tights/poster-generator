import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

LIBRARY_NAME = "Poster Generator"
LIBRARY_SLUG = "poster-generator"

def get_logger():
    return logging.getLogger(LIBRARY_SLUG)

DEFAULT_FONT = Path(__file__).parent / "fonts" / "open_sans.ttf"
