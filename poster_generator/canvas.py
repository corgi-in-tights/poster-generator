from PIL import Image, ImageDraw

from .settings import get_logger

logger = get_logger()

class Canvas:
    def __init__(self, width=1080, height=1350, background="#fff", size=None):
        self.width = size[0] if size else width
        self.height = size[1] if size else height
        
        self._image = Image.new("RGB", (self.width, self.height), background)
        self._draw = ImageDraw.Draw(self._image)
        self._elements = {}

    def add_element(self, identifier, element):
        if identifier in self._elements:
            raise ValueError(f"Element with identifier '{identifier}' already exists.")
        self._elements[identifier] = element

    def render(self, global_op=None):
        for k, e in self._elements.items():
            if e.is_ready():
                if global_op is not None:
                    global_op(e)
                e.draw(self._draw, self._image)
                
            else:
                logger.warning(f"Element '{k}' is not ready and will be skipped.")
               
        return self._image
