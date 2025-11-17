from PIL import Image
from .element import CanvasElement
import colorsys

class ImageElement(CanvasElement):
    def __init__(self, image_path=None, position=None, size=None):
        self.image_path = image_path
        self.position = position
        self.size = size
        self.image = None
        if image_path:
            self.load_image(image_path)


    def load_image(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGBA")
    
        if self.size:
            self.image = self.image.resize(self.size)

    def apply_hue_shift(self, hue_shift):
        pixels = self.image.load()
        width, height = self.image.size
        
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                h = (h + hue_shift / 360.0) % 1.0
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)


    def draw(self, draw, canvas_image, position=None):
        position = position if position else self.position if self.position else None
        if position is None:
            raise ValueError("Position must be specified to draw the image element as (x, y).")
        
        pos2 = (position[0] + self.size[0], position[1] + self.size[1])
        
        if self.image is None:
            raise ValueError("No image loaded to draw.")
        
        out = self.image.split()
        canvas_image.paste(self.image, (*position, *pos2), out[3])


    def is_ready(self):
        return self.image is not None
