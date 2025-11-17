from PIL import ImageFont
from typing import TYPE_CHECKING
from .element import CanvasElement
from poster_generator.settings import DEFAULT_FONT

if TYPE_CHECKING:
    from PIL import ImageDraw


class TextElement(CanvasElement):
    def __init__(self, text=None, font_path=None, font_size=20, color="#000", position=None):
        self.text = text
        self.font_path = font_path or DEFAULT_FONT
        self.font_size = font_size
        self.color = color
        self.position = position

        # Always load a real TTF so size works
        self.font = ImageFont.truetype(self.font_path, self.font_size)

    def draw(self, draw: "ImageDraw.Draw", image, position=None):
        position = position or self.position
        if position is None:
            raise ValueError("Position must be specified as (x, y).")

        draw.text(position, self.text, font=self.font, fill=self.color)

    def is_ready(self):
        return self.text is not None and self.font is not None