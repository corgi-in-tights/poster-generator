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

    def apply_hue_shift(self, degrees: float):
        img = self.image.convert("RGBA")
        hsv = img.convert("HSV")
        
        h, s, v = hsv.split()
        hue_shift_pixels = h.point(lambda p: (p + int(degrees * 255 / 360)) % 256)
        
        hsv = Image.merge("HSV", (hue_shift_pixels, s, v))
        
        self.image = hsv.convert("RGBA")
        
    def set_hue_from_hex(self, hex_color: str):
        hex_color = hex_color.lstrip("#")
        r_hex = int(hex_color[0:2], 16)
        g_hex = int(hex_color[2:4], 16)
        b_hex = int(hex_color[4:6], 16)

        # Convert hex target to HSV → we only keep Hue
        target_h, _, _ = colorsys.rgb_to_hsv(
            r_hex / 255.0, g_hex / 255.0, b_hex / 255.0
        )

        # Make sure working in RGBA
        self.image = self.image.convert("RGBA")
        pixels = self.image.load()

        width, height = self.image.size

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]

                # convert pixel to HSV
                h, s, v = colorsys.rgb_to_hsv(
                    r / 255.0, g / 255.0, b / 255.0
                )

                # replace hue
                h = target_h

                # convert back to RGB
                r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)

                pixels[x, y] = (
                    int(r2 * 255),
                    int(g2 * 255),
                    int(b2 * 255),
                    a,
                )
        
    
    def draw(self, draw, canvas_image, position=None):
        position = position if position else self.position if self.position else None
        if position is None:
            raise ValueError("Position must be specified to draw the image element as (x, y).")
        
        pos2 = (position[0] + self.size[0], position[1] + self.size[1])
        
        if self.image is None:
            raise ValueError("No image loaded to draw.")
        
        out = self.image.split()
        canvas_image.paste(self.image, (*position, *pos2), out[3])

    def apply_operation(self, operation):
        self.image = operation(self.image)
        
    def is_ready(self):
        return self.image is not None
