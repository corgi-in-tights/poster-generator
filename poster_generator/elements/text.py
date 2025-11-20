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
        draw.text(self.position, self.text, font=self.font, fill=self.color)

    def is_ready(self):
        """
        Check if the text element is ready to be drawn.
        
        Returns:
            bool: True if text and font are loaded.
        """
        return self.text is not None and self.font is not None
    
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        return False
    
    def apply_operation(self, operation):
        old_font_size = self.font_size
        
        res = operation({
            "text": self.text,
            "font_size": self.font_size,
            "color": self.color
        })
        self.text = res["text"]
        self.font_size = res["font_size"]
        self.color = res["color"]
        
        # update font if it changed
        if old_font_size != self.font_size:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
