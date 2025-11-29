import logging
import platform
from pathlib import Path

from PIL import ImageFont

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent

class FontManager:
    DEFAULT_FONT_PATH = ROOT_DIR / "resources/fonts/open_sans.ttf"

    def __init__(self):
        self.font_families = {}
        self.font_cache = {}

        self._register_inbuilt_fonts()
        self._register_system_fonts()

    def _register_inbuilt_fonts(self):
        self.register_font_family("Open Sans", FontManager.DEFAULT_FONT_PATH)
        self.register_font_family("Bebas Neue Regular", ROOT_DIR / "resources/fonts/bebas_neue_regular.ttf",
                                  alternate_names=["Bebas Neue"])

    def _register_system_fonts(self):
        """Register system-installed font families."""
        system = platform.system()

        if system == "Windows":
            dirs = [Path(r"C:\Windows\Fonts")]
        elif system == "Darwin":  # Mac
            dirs = [
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path("~/Library/Fonts").expanduser(),
            ]
        else:  # Unix/Linux
            dirs = [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path("~/.fonts").expanduser(),
                Path("~/.local/share/fonts").expanduser(),
            ]

        exts = {".ttf", ".otf", ".ttc", ".otc"}

        for d in dirs:
            if d.exists():
                for p in d.rglob("*"):
                    if p.suffix.lower() in exts:
                        family_name = p.stem
                        self.register_font_family(family_name, p)

        logger.info("Registered %d system font families.", len(self.font_families))
        logger.debug("Font families: %s", list(self.font_families.keys()))

    def register_font_family(self, family_name: str, font_path: str | Path, alternate_names: list[str] | None = None):
        """Register a new font family.

        Args:
            family_name (str): Name of the font family.
            font_path (str or Path): Path to the TrueType font file.
        """
        self.font_families[family_name.lower()] = Path(font_path)
        if alternate_names:
            for alt_name in alternate_names:
                self.font_families[alt_name.lower()] = Path(font_path)

    def get_font(self, family_name: str, font_size: int):
        """Retrieve a font from the cache or load it if not cached.

        Args:
            family_name (str): Name of the font family.
            font_size (int): Size of the font in points.

        Returns:
            ImageFont.FreeTypeFont: Loaded font object.
        """
        if family_name is None:
            msg = "Font family name cannot be None, given: ", family_name
            raise ValueError(msg)

        font_path = self.font_families.get(family_name.lower())
        if font_path is None:
            logger.warning("Font family '%s' not found. Using default font.", family_name)
            font_path = FontManager.DEFAULT_FONT_PATH

        if not font_path.exists():
            logger.warning("Font file '%s' does not exist. Using default font.", font_path)
            font_path = FontManager.DEFAULT_FONT_PATH

        cache_key = (font_path, font_size)

        if cache_key not in self.font_cache:
            font = ImageFont.truetype(str(font_path), font_size)
            self.font_cache[cache_key] = font

        return self.font_cache[cache_key]

    def get_all_families(self) -> list[str]:
        """Get a list of all registered font family names.

        Returns:
            list[str]: List of font family names.
        """
        return list(self.font_families.keys())

_manager_instance = FontManager()

def get_font_manager() -> FontManager:
    """Get the global FontManager instance.

    Returns:
        FontManager: The global font manager.
    """
    return _manager_instance

def register_font_family(family_name: str, font_path: str | Path):
    """Register a new font family in the global FontManager.

    Args:
        family_name (str): Name of the font family.
        font_path (str or Path): Path to the TrueType font file.
    """
    _manager_instance.register_font_family(family_name, font_path)
