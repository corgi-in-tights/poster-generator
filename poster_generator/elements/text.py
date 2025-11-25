import logging
from PIL import ImageFont
from typing import TYPE_CHECKING
from .drawable import DrawableElement
from pathlib import Path

if TYPE_CHECKING:
    from PIL import ImageDraw

DEFAULT_FONT = Path(__file__).parent.parent / "resources/fonts/open_sans.ttf"

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
        color (str): Text color in hex format (e.g., "#000000").
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
        ...     color="#FF0000"
        ... )
        >>> my_text.update_text("New text content")
    """
    font_cache = {}
    
    def __init__(self, position, text="", font_path=None, font_size=20, max_width=None, wrap_style="word", text_alignment="left", color="#000"):
        """Initialize a TextElement with specified properties.
        
        Args:
            position (tuple): The (x, y) coordinates for positioning the text element.
            text (str, optional): The text content to display. Defaults to "".
            font_path (str, optional): Path to the font file. If None, uses DEFAULT_FONT. Defaults to None.
            font_size (int, optional): Size of the font in points. Defaults to 20.
            max_width (int, optional): Maximum width for text wrapping. If None, no wrapping is applied. Defaults to None.
            wrap_style (str, optional): Style of text wrapping - "word", "char", or "none". Defaults to "word".
            text_alignment (str, optional): Text alignment - "center", "left", or "right". Defaults to "left".
            color (str, optional): Text color in hex format (e.g., "#000000"). Defaults to "#000".
        """
        super().__init__(position)
        self.font_path = font_path or DEFAULT_FONT
        self.font_size = font_size
        self.max_width = max_width
        self.wrap_style = wrap_style
        self.color = color
        self.text_alignment = text_alignment
        
        self._reset_font()
        self.update_text(text)
        
    def _reset_font(self):
        """Reset the font object based on current font_path and font_size."""
        fk = (self.font_path, self.font_size)
        
        # Attempt to cache across instances to avoid reloading same font multiple times
        if fk in (TextElement.font_cache or {}):
            self.font = TextElement.font_cache[fk]
        else:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            TextElement.font_cache[(self.font_path, self.font_size)] = self.font
    
    def update_text(self, t: str):
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
            tokens = list(text)                    # ["H","e","l","l","o"]
            joiner = ""                            # no space between chars
        elif self.wrap_style == "word":
            tokens = text.split()                  # ["Hello","world"]
            joiner = " "                            # space between words
        else:
            logger.warning(f"Unknown wrap_style '{self.wrap_style}' for TextElement, defaulting to no wrapping.")
            return text

        lines = []
        current = []

        for token in tokens:
            # Try adding the next token
            test_line = joiner.join(current + [token])
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

        # bbox = (left, top, right, bottom)
        bbox = self.font.getbbox(self.text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return (width, height)

    def draw(self, draw: "ImageDraw.Draw", _, blend_settings: dict):
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
            raise ValueError("No position specified for TextElement drawing.")
        draw.text(self.position, self.text, font=self.font, fill=self.color, align=self.text_alignment)

    def is_ready(self):
        """
        Check if the text element is ready to be drawn.
        
        Returns:
            bool: True if text and font are loaded.
        """
        return self.text is not None and self.font is not None
    
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        width, height = self.get_size()
        return not (x2 < self.position[0] or
                    x1 > self.position[0] + width or
                    y2 < self.position[1] or
                    y1 > self.position[1] + height)
    
    
    def apply_operation(self, operation):
        old_font_size = self.font_size
        old_font_path = self.font_path
        
        result = operation({
            "position": self.position,
            "text": self.text,
            "font_size": self.font_size,
            "font_path": self.font_path,
            "color": self.color,
            "max_width": self.max_width,
            "wrap_style": self.wrap_style,
            "text_alignment": self.text_alignment
        })
        self.update_position(result.get("position", self.position))
        self.font_size = result["font_size"]
        self.font_path = result["font_path"]
        self.color = result["color"]
        self.max_width = result["max_width"]
        self.wrap_style = result["wrap_style"]
        self.text_alignment = result["text_alignment"]
        
        # update font if it changed
        if old_font_size != self.font_size or old_font_path != self.font_path:
            self._reset_font()

        if (result["text"] != self.text or
            self.max_width != result["max_width"] or 
            self.wrap_style != result["wrap_style"] or
            self.text_alignment != result["text_alignment"]):
            
            self.update_text(result["text"])