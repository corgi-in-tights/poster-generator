from PIL import Image
from .drawable import DrawableElement
import colorsys

class ImageElement(DrawableElement):
    def __init__(self, position, image_path=None, width=None, height=None):
        super().__init__(position)
        self.image_path = image_path
        self.width = width
        self.height = height
        self.image = None
        if image_path:
            self.load_image(image_path)


    def load_image(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGBA")
    
        if self.width or self.height:
            self.image = self.image.resize((self.width, self.height))

    def apply_hue_shift(self, degrees: float):
        img = self.image.convert("RGBA")
        hsv = img.convert("HSV")
        
        h, s, v = hsv.split()
        hue_shift_pixels = h.point(lambda p: (p + int(degrees * 255 / 360)) % 256)
        
        hsv = Image.merge("HSV", (hue_shift_pixels, s, v))
        
        self.image = hsv.convert("RGBA")
        
    def set_hue_from_hex(self, hex_color: str):
        """
        Replace the hue of all pixels with the hue from a hex color.
        
        Preserves the saturation and value of each pixel while replacing only the hue
        component with the hue from the specified hex color.
        
        Args:
            hex_color: Hex color string (e.g., "#FF5733" or "FF5733").
        """
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
        
    
    def draw(self, draw, canvas_image, position=None, opacity=1.0):
        """
        Draw the image onto the canvas with alpha blending.
        
        Args:
            draw: PIL ImageDraw instance (not used for image drawing).
            canvas_image: PIL Image instance representing the canvas.
            position: Optional (x, y) tuple to override the element's position.
        
        Raises:
            ValueError: If no position is specified or no image is loaded.
        """
        position = position if position else self.position if self.position else None
        if position is None:
            raise ValueError("Position must be specified to draw the image element as (x, y).")
        
        pos2 = (position[0] + self.width if self.width else 0, 
                position[1] + self.height if self.height else 0)
        
        if self.image is None:
            raise ValueError("No image loaded to draw.")
        
        out = self.image.split()
        canvas_image.paste(self.image, (*position, *pos2), out[3])

    def apply_operation(self, operation):
        """
        Apply a transformation operation to the image.
        
        Args:
            operation: Callable that takes a PIL Image and returns a transformed PIL Image.
        """
        self.image = operation(self.image)
        
    def is_ready(self):
        """
        Check if the image element is ready to be drawn.
        
        Returns:
            bool: True if an image is loaded.
        """
        return self.image is not None

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        return False
    