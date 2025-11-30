import logging

from PIL import Image, ImageDraw

from poster_generator.elements.abstract import DrawableElement
from poster_generator.utils import normalize_color

from .fonts import get_font_manager

logger = logging.getLogger(__name__)


class TextElement(DrawableElement):
    """A drawable text element with support for wrapping, alignment, and fonts.

    Attributes:
        font_size (int): The font size in points.
        max_width (int): Maximum width for text wrapping.
        wrap_style (str): Text wrapping style.
        fill (str): Normalized color value for the text.
        text_alignment (str): Text alignment style.
        width (int): Calculated width of the text element (initialized to 0).
        height (int): Calculated height of the text element (initialized to 0).

    Example:
        >>> my_text = TextElement(
        ...     position=(100, 100),
        ...     text="Hello World",
        ...     font_size=24,
        ...     max_width=200,
        ...     fill="#FF0000",
        ...     text_alignment="center"
        ... )
        >>> my_text.set_text_content("New text content")
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
        """
        Initialize a text element with specified styling and positioning.

        Args:
            text (str): The text content to display. Defaults to "".
            font_family (str): The font family name to use. Defaults to "Open Sans".
            font_size (int): The size of the font in points. Defaults to 20.
            max_width (int): Maximum width for text wrapping in pixels. Defaults to None.
            wrap_style (str): The text wrapping style ("word" or "char"). Defaults to "word".
            text_alignment (str):
                Horizontal text alignment ("left", "center", or "right"). Defaults to "left".
            fill (str | list | dict | None): The color of the text (hex, rgb, or color name). Defaults to "#000".
            **kwargs: Additional keyword arguments passed to the DrawableElement constructor.
        """
        super().__init__(position)
        self.font_size = font_size
        self.font_family = font_family
        self.max_width = max_width
        self.wrap_style = wrap_style
        self.fill = normalize_color(fill)
        self.text_alignment = text_alignment

        # before calculations
        self.width = 0
        self.height = 0

        self.set_font(font_family, font_size)
        self.set_text_content(text)

    def set_font(self, font_family: str | None = None, size: int | None = None):
        """
        Set the font family and size for the TextElement.

        Args:
            font_family (str | None): The font family name to use. If None, uses current font family.
            size (int | None): The size of the font in points. If None, uses current font size.
        """
        self.font = get_font_manager().get_font(font_family or self.font.family, size or self.font_size)
        if font_family is not None:
            self.font_family = font_family
        if size is not None:
            self.font_size = size

    def set_text_content(self, t: str):
        """
        Set the text content of the TextElement, applying wrapping if necessary.

        Args:
            t (str): The text content to set.
        """
        if t == "":
            self.text_content = ""
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

        self.text_content = "\n".join(lines)
        logger.debug("Text set to: %s", self.text_content.replace("\n", "\\n"))
        self.width = curr_width
        self.height = curr_height

    def _wrap_text(self, text):
        # It's easier to just test each case rather than try to do complex calculations
        # Not too computationally expensive for typical text sizes
        if self.wrap_style is None or self.wrap_style == "none":
            return text

        logger.debug(
            "Wrapping text for TextElement with max_width=%s and wrap_style=%s",
            self.max_width,
            self.wrap_style,
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
        if not self.text_content or self.font is None:
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

        image_draw.text(self.position, self.text_content, font=self.font, fill=self.fill, align=self.text_alignment)

        image.alpha_composite(alpha_image)

    def is_ready(self):
        """
        Check if the text element is ready to be drawn.

        Returns:
            bool: True if text and font are loaded.
        """
        return self.font is not None and self.text_content is not None and self.text_content != ""

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """
        Check if this text element overlaps with a rectangular region.

        Args:
            x1 (float): Left edge of the query region.
            y1 (float): Top edge of the query region.
            x2 (float): Right edge of the query region.
            y2 (float): Bottom edge of the query region.
        """
        width, height = self.get_size()
        return not (
            x2 < self.position[0]
            or x1 > self.position[0] + width
            or y2 < self.position[1]
            or y1 > self.position[1] + height
        )
