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
    FONT_CACHE = {}
    
    def __init__(self, position, text="", font_path=None, font_size=20, max_width=None, wrap_style="word", color="#000"):
        super().__init__(position)
        self.font_path = font_path or DEFAULT_FONT
        self.font_size = font_size
        self.max_width = max_width
        self.wrap_style = wrap_style
        self.color = color
        
        # Attempt to cache across instances to avoid reloading same font multiple times
        fk = (self.font_path, self.font_size)
        if fk in (TextElement.FONT_CACHE or {}):
            self.font = TextElement.FONT_CACHE[fk]
        else:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
            TextElement.FONT_CACHE[(self.font_path, self.font_size)] = self.font
            
        self.update_text(text)
            
    
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
        draw.text(self.position, self.text, font=self.font, fill=self.color)

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
        
        res = operation({
            "text": self.text,
            "font_size": self.font_size,
            "font_path": self.font_path,
            "color": self.color
        })
        self.update_text(res["text"])
        self.font_size = res["font_size"]
        self.font_path = res["font_path"]
        self.color = res["color"]
        
        # update font if it changed
        if old_font_size != self.font_size or old_font_path != self.font_path:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
