from PIL import Image
from .drawable import DrawableElement

class ImageElement(DrawableElement):
    def __init__(self, position, image_path=None, width=None, height=None):
        super().__init__(position)
        self.image_path = image_path
        self.width = width
        self.height = height
        
        self.image = None
        if image_path:
            self._load_image(image_path)

    def _load_image(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGBA")
    
        if self.width or self.height:
            self.image = self.image.resize((self.width, self.height))
            
        # Set from image
        if self.width is None:
            self.width = self.image.width
        if self.height is None:
            self.height = self.image.height
        
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
        return (
            self.position[0] <= x1 <= self.position[0] + (self.width or 0) and
            self.position[1] <= y1 <= self.position[1] + (self.height or 0) and
            self.position[0] <= x2 <= self.position[0] + (self.width or 0) and
            self.position[1] <= y2 <= self.position[1] + (self.height or 0)
        )
    