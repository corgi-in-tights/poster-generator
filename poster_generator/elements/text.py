import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import ImageFont

from .drawable import DrawableElement

if TYPE_CHECKING:
    from PIL import ImageDraw

DEFAULT_FONT = Path(__file__).parent.parent / "resources/fonts/open_sans.ttf"

FONT_FAMILIES = {
    "Open Sans": DEFAULT_FONT,
}

logger = logging.getLogger(__name__)


class TextElement(DrawableElement):
    """A drawable text element with support for wrapping, alignment, and font caching.

    This class extends DrawableElement to provide text rendering capabilities including
    automatic text wrapping (word or character-based), text alignment (left, center, right),
    font caching for performance optimization, and customizable font, size, and color.

    Class Attributes:
        font_cache (dict): Cache storing fonts by (font_path, font_size).

    Attributes:
        font_path (str): Path to the TrueType font file being used.
        font_size (int): Size of the font in points.
        max_width (int or None): Maximum width in pixels for text wrapping.
        wrap_style (str): Text wrapping style - "word", "char", or "none".
        fill (str): Text color in hex format (e.g., "#000000").
        text_alignment (str): Text alignment style - "center", "left", or "right".
        font (ImageFont.FreeTypeFont): PIL ImageFont object for rendering.
        text (str): The actual text content, possibly wrapped.

    Example:
        >>> my_text = TextElement(
        ...     position=(100, 100),
        ...     text="Hello World",
        ...     font_size=24,
        ...     max_width=200,
        ...     wrap_style="word",
        ...     fill="#FF0000"
        ... )
        >>> my_text.set_text("New text content")
    """

    font_cache = {}

    def __init__(
        self,
        position=(0, 0),
        text="",
        font_path=None,
        font_family="Open Sans",
        font_size=20,
        max_width=None,
        wrap_style="word",
        text_alignment="left",
        fill="#000",
    ):
        """Initialize a TextElement with specified properties.

        Args:
            position (tuple): The (x, y) coordinates for positioning the text element.
            text (str, optional): The text content to display. Defaults to "".
            font_path (str, optional):
                Path to the font file. If None, uses DEFAULT_FONT. Defaults to None. Overrides font_family.
            font_family (str, optional): Used to select from in-built fonts, library default (open sans).
            font_size (int, optional): Size of the font in points. Defaults to 20.
            max_width (int, optional):
                Maximum width for text wrapping. If None, no wrapping is applied. Defaults to None.
            wrap_style (str, optional): Style of text wrapping - "word", "char", or "none". Defaults to "word".
            text_alignment (str, optional): Text alignment - "center", "left", or "right". Defaults to "left".
            fill (str, optional): Text color in hex format (e.g., "#000000"). Defaults to "#000".
        """
        super().__init__(position)
        self.font_path = font_path or FONT_FAMILIES.get(font_family, DEFAULT_FONT)
        self.font_size = font_size
        self.max_width = max_width
        self.wrap_style = wrap_style
        self.fill = fill
        self.text_alignment = text_alignment

        self._reset_font(font_path)
        self.set_text(text)

    def _reset_font(self, font_path):
        """Reset the font object based on current font_path and font_size."""
        fk = (font_path, self.font_size)

        # Attempt to cache across instances to avoid reloading same font multiple times
        if fk in (TextElement.font_cache or {}):
            self.font = TextElement.font_cache[fk]
        else:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            TextElement.font_cache[(self.font_path, self.font_size)] = self.font

    def set_font_size(self, font_size: int):
        """
        Set the font size and update the font object.

        Args:
            font_size (int): The new font size in points.
        """
        self.font_size = font_size
        self._reset_font(self.font_path)

    def set_font_path(self, font_path: str):
        """
        Set the font path and update the font object.

        Args:
            font_path (str): The new font file path.
        """
        self.font_path = font_path
        self._reset_font(self.font_path)

    def set_text(self, t: str):
        """
        Set the text content of the TextElement, applying wrapping if necessary.

        Args:
            t (str): The text content to set.
        """
        self.text = self._wrap_text(t, self.max_width) if self.max_width else t

    def _wrap_text(self, text, max_width):
        # It's easier to just test each case rather than try to do complex calculations
        # Not too computationally expensive for typical text sizes
        if self.max_width is None or self.wrap_style is None or self.wrap_style == "none":
            return text

        # Choose tokens: words or chars
        if self.wrap_style == "char":
            tokens = list(text)  # ["H","e","l","l","o"]
            joiner = ""  # no space between chars
        elif self.wrap_style == "word":
            tokens = text.split()  # ["Hello","world"]
            joiner = " "  # space between words
        else:
            logger.warning("Unknown wrap_style '%s' for TextElement, defaulting to no wrapping.", self.wrap_style)
            return text

        lines = []
        current = []

        for token in tokens:
            # Try adding the next token
            test_line = joiner.join([*current, token])
            w = self.font.getlength(test_line)

            if w <= max_width or not current:
                current.append(token)
            else:
                # commit line
                lines.append(joiner.join(current))
                current = [token]

        if current:
            lines.append(joiner.join(current))

        return "\n".join(lines)

    def _wrap_text_char(self, text, max_width):
        lines = []
        current = ""

        for char in text:
            test_line = current + char
            w = self.font.getlength(test_line)

            if w <= max_width or not current:
                current += char
            else:
                # Break line
                lines.append(current)
                current = char

        if current:
            lines.append(current)

        return "\n".join(lines)

    def get_size(self):
        """
        Return the pixel width/height of the rendered text.

        Returns:
            (width, height): Tuple of width and height in pixels.
        """
        if not self.text:
            return (0, 0)

        # equal to (left, top, right, bottom)
        bbox = self.font.getbbox(self.text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return (width, height)

    def draw(self, draw: "ImageDraw.Draw", _, blend_settings: dict | None = None):
        """
        Draw the text onto the canvas.

        Args:
            draw: PIL ImageDraw instance for drawing operations.
            image: PIL Image instance (not used for text drawing).
            position: Optional (x, y) tuple to override the element's position.

        Raises:
            ValueError: If no position is specified either as parameter or in the element.
        """
        if self.position is None:
            msg = "No position specified for TextElement drawing."
            raise ValueError(msg)
        draw.text(self.position, self.text, font=self.font, fill=self.fill, align=self.text_alignment)

    def is_ready(self):
        """
        Check if the text element is ready to be drawn.

        Returns:
            bool: True if text and font are loaded.
        """
        return self.font is not None and self.text is not None and self.text != ""

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        width, height = self.get_size()
        return not (
            x2 < self.position[0]
            or x1 > self.position[0] + width
            or y2 < self.position[1]
            or y1 > self.position[1] + height
        )
