from PIL import ImageFont
from typing import TYPE_CHECKING
from .drawable import DrawableElement
from poster_generator.settings import DEFAULT_FONT

if TYPE_CHECKING:
    from PIL import ImageDraw


class TextElement(DrawableElement):
    def __init__(self, position, text=None, font_path=None, font_size=20, color="#000"):
        super().__init__(position)
        self.text = text
        self.font_path = font_path or DEFAULT_FONT
        self.font_size = font_size
        self.color = color

        # Always load a real TTF so size works
        self.font = ImageFont.truetype(self.font_path, self.font_size)

    def draw(self, image_draw: "ImageDraw.Draw", image, position=None):
        position = position or self.position
        if position is None:
            raise ValueError("Position must be specified as (x, y).")

        image_draw.text(position, self.text, font=self.font, fill=self.color)

    def is_ready(self):
        return self.text is not None and self.font is not None
    
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        return False
    
    def apply_operation(self, operation):
        self.text = operation(self.text)