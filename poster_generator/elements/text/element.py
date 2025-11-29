import logging
from pathlib import Path

from PIL import Image, ImageDraw

from poster_generator.elements.abstract import DrawableElement
from poster_generator.utils import normalize_color

from .fonts import get_font_manager

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

    def __init__(  # noqa: PLR0913
        self,
        *,
        position=(0, 0),
        text="",
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
        self.font_size = font_size
        self.max_width = max_width
        self.wrap_style = wrap_style
        self.fill = normalize_color(fill)
        self.text_alignment = text_alignment

        # before calculations
        self.width = 0
        self.height = 0

        self.set_font(font_family, font_size)
        self.set_text(text)

    def set_font(self, font_family: str, size: int | None = None):
        self.font = get_font_manager().get_font(font_family, size or self.font_size)

    def set_font_size(self, font_size: int):
        """
        Set the font size and update the font object.

        Args:
            font_size (int): The new font size in points.
        """
        self.font_size = font_size
        self._reset_font(self.font_path)

    def set_text(self, t: str):
        """
        Set the text content of the TextElement, applying wrapping if necessary.

        Args:
            t (str): The text content to set.
        """
        if t == "":
            self.text = ""
            self.width = 0
            self.height = 0
            return

        logger.debug("Setting text for TextElement: %s", t._identifier if hasattr(t, "_identifier") else t)  # noqa: SLF001
        lines = self._wrap_text(t) if self.max_width else [t]

        curr_width = 0
        curr_height = 0

        for li in lines:
            w, h = self.font.getbbox(li)[2:]
            curr_width = max(curr_width, w)
            curr_height += h

        self.text = "\n".join(lines)
        logger.debug("Text set to: %s", self.text.replace("\n", "\\n"))
        self.width = curr_width
        self.height = curr_height

    def _wrap_text(self, text):
        # It's easier to just test each case rather than try to do complex calculations
        # Not too computationally expensive for typical text sizes
        if self.wrap_style is None or self.wrap_style == "none":
            return text

        logger.debug(
            "Wrapping text for TextElement with max_width=%s and wrap_style=%s", self.max_width, self.wrap_style,
        )

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

            if w <= self.max_width or not current:
                current.append(token)
            else:
                # commit line
                lines.append(joiner.join(current))
                current = [token]

        if current:
            lines.append(joiner.join(current))

        logger.debug("Wrapped text lines: %s", lines)

        return lines

    def _wrap_text_char(self, text):
        lines = []
        current = ""

        for char in text:
            test_line = current + char
            w = self.font.getlength(test_line)

            if w <= self.max_width or not current:
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
        if not self.text or self.font is None:
            return (0, 0)

        return (self.width, self.height)

    def draw(self, image_draw: "ImageDraw.Draw", image, blend_settings: dict | None = None):
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

        opacity_modifier = (blend_settings or {}).get("opacity", 1.0)
        self.fill = self.apply_opacity_modifier(self.fill, opacity_modifier)

        alpha_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        image_draw = ImageDraw.Draw(alpha_image, "RGBA")

        image_draw.text(self.position, self.text, font=self.font, fill=self.fill, align=self.text_alignment)

        image.alpha_composite(alpha_image)

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
