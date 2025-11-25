"""Rectangle element implementation for rendering filled rectangles on canvas."""

from PIL import ImageDraw
from typing import TYPE_CHECKING
from .drawable import DrawableElement

if TYPE_CHECKING:
    from PIL import Image


class RectangleElement(DrawableElement):
    """A drawable rectangle element with support for rounded corners and styling.
    
    The rectangle is positioned by its top-left corner and can have rounded corners
    specified by a radius parameter. Supports both background and outline colors.
    
    Attributes:
        width (int): Rectangle width in pixels.
        height (int): Rectangle height in pixels.
        background (str): background color as hex string (e.g., "#FF5733").
        outline_color (str or None): Outline color as hex string, or None for no outline.
        outline_width (int): Width of the outline in pixels.
        radius (int): Corner radius in pixels for rounded corners (0 for sharp corners).
    
    Example:
        >>> rect = RectangleElement(
        ...     position=(100, 100),
        ...     width=300,
        ...     height=200,
        ...     background="#FF5733"
        ... )
        >>> 
        >>> rounded_rect = RectangleElement(
        ...     position=(100, 100),
        ...     width=300,
        ...     height=200,
        ...     background="#3498db",
        ...     outline="#2c3e50",
        ...     outline_width=3,
        ...     radius=20
        ... )
    """
    
    def __init__(
        self,
        position,
        width=100,
        height=100,
        background="#000000",
        outline_color=None,
        outline_width=1,
        radius=0,
        other_position=None
    ):
        """Initialize a RectangleElement with specified dimensions and styling.
        
        Args:
            position (tuple): The (x, y) coordinates for the top-left corner of the rectangle.
            width (int, optional): Width of the rectangle in pixels. Defaults to 100.
            height (int, optional): Height of the rectangle in pixels. Defaults to 100.
            background (str, optional): background color as hex string. Defaults to "#000000".
            outline (str, optional): Outline color as hex string. Defaults to None (no outline).
            outline_width (int, optional): Width of the outline in pixels. Defaults to 1.
            radius (int, optional): Corner radius for rounded corners in pixels. Defaults to 0 (sharp corners).
            other_position (tuple, optional): Calculates width and height based on this position if provided.
        """
        super().__init__(position)
        if other_position is not None:
            width = abs(other_position[0] - position[0])
            height = abs(other_position[1] - position[1])
        self.width = width
        self.height = height
        
        self.background = background
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.radius = radius
    
    def draw(self, image_draw: "ImageDraw.Draw", image: "Image.Image", blend_settings: dict) -> None:
        """
        Draw the rectangle onto the canvas.
        
        Args:
            image_draw: PIL ImageDraw instance for drawing operations.
            image: PIL Image instance representing the canvas (not used for rectangles).
            blend_settings: Dictionary containing blend settings (opacity, etc.).
        
        Raises:
            ValueError: If position is not set.
        """
        if self.position is None:
            raise ValueError("Position must be specified as (x, y).")
        
        x, y = self.position
        x2 = x + self.width
        y2 = y + self.height
        
        # Draw rounded rectangle if radius is specified
        if self.radius > 0:
            image_draw.rounded_rectangle(
                [(x, y), (x2, y2)],
                radius=self.radius,
                fill=self.background,
                outline=self.outline_color,
                width=self.outline_width
            )
        else:
            # Draw regular rectangle
            image_draw.rectangle(
                [(x, y), (x2, y2)],
                fill=self.background,
                outline=self.outline_color,
                width=self.outline_width
            )
    
    def is_ready(self) -> bool:
        """
        Check if the rectangle element is ready to be drawn.
        
        Returns:
            bool: True if position, width, and height are set.
        """
        return (
            self.position is not None
            and self.width is not None
            and self.height is not None
        )
    
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """
        Check if this rectangle overlaps with a rectangular region.
        
        Args:
            x1: Left edge of the query region.
            y1: Top edge of the query region.
            x2: Right edge of the query region.
            y2: Bottom edge of the query region.
        
        Returns:
            bool: True if the rectangle overlaps with the specified region.
        """
        if self.position is None:
            return False
        
        rect_x1, rect_y1 = self.position
        rect_x2 = rect_x1 + self.width
        rect_y2 = rect_y1 + self.height
        
        # Check if rectangles overlap
        return not (
            rect_x2 < x1 or  # Rectangle is to the left of region
            rect_x1 > x2 or  # Rectangle is to the right of region
            rect_y2 < y1 or  # Rectangle is above region
            rect_y1 > y2     # Rectangle is below region
        )
    
    def apply_operation(self, operation):
        """
        Apply a transformation operation to the rectangle.
        
        Note: This is a placeholder for interface compatibility.
        Rectangles are vector shapes and don't support image operations.
        
        Args:
            operation: Callable that would transform the element (not applicable to rectangles).
        """
        result = operation({
            "position": self.position,
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "outline_color": self.outline_color,
            "outline_width": self.outline_width,
            "radius": self.radius
        })
        
        self.position = result.get("position", self.position)
        self.width = result.get("width", self.width)
        self.height = result.get("height", self.height)
        self.background = result.get("background", self.background)
        self.outline_color = result.get("outline", self.outline_color)
        self.outline_width = result.get("outline_width", self.outline_width)
        self.radius = result.get("radius", self.radius)
    
    def get_size(self):
        """
        Get the dimensions of the rectangle.
        
        Returns:
            tuple: (width, height) of the rectangle.
        """
        return (self.width, self.height)