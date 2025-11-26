from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..snapping import get_alignment_position

if TYPE_CHECKING:
    from PIL import Image, ImageDraw
    from ..canvas import Canvas
    
class DrawableElement(ABC):
    """Abstract base class for all drawable elements in a poster.
    
    This class defines the interface for all drawable elements that can be positioned
    and rendered on an image. Subclasses must implement methods for drawing, checking
    readiness, detecting overlaps, and applying operations.
    
    Attributes:
        position (tuple): The (x, y) coordinates of the element on the canvas.
    """
    
    def __init__(self, position):
        """Initialize a DrawableElement with a position.
        
        Args:
            position (tuple): The (x, y) coordinates for the element.
        """
        self.position = position
    
    @abstractmethod
    def draw(self, image_draw: "ImageDraw.Draw", image: "Image.Image", blend_settings: dict) -> None:
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        pass

    @abstractmethod
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        pass
    
    def overlaps_at(self, x: float, y: float) -> bool:
        """
        Check if this drawable overlaps with a point at the given coordinates.

        Args:
            x (float): The x-coordinate of the point to check.
            y (float): The y-coordinate of the point to check.

        Returns:
            bool: True if the drawable overlaps with the point, False otherwise.

        Note:
            This method uses a small epsilon value (1e-5) to create a tiny region
            around the point and checks if the drawable overlaps with that region.
        """
        eps = 1e-5
        return self.overlaps_region(x, y, x + eps, y + eps)

    @abstractmethod
    def apply_operation(self, operation):
        pass
    
    @abstractmethod
    def get_size(self):
        """
        Return the pixel width/height of the drawable element.

        Returns:
            (width, height): Tuple of width and height in pixels.
        """
        pass
    
    def update_position(self, position):
        """
        Update the position of the drawable element.

        Args:
            position: New position to set for the drawable element.
        """
        if position is not None:
            self.position = position
        
    def translate(self, dx: float, dy: float):
        """
        Translate the position of the drawable element by the given offsets.

        Args:
            dx (float): Offset in the x-direction.
            dy (float): Offset in the y-direction.
        """
        self.position = (self.position[0] + dx, self.position[1] + dy)
        
    def snap_to(self, canvas: "Canvas", x_align: str = "auto", y_align: str = "auto"):
        if x_align not in ["auto", "left", "center", "right"]:
            raise ValueError(f"Invalid x_align value: {x_align}")
        if y_align not in ["auto", "top", "center", "bottom"]:
            raise ValueError(f"Invalid y_align value: {y_align}")
        
        width, height = self.get_size()
        
        pos = get_alignment_position(
            canvas.width,
            canvas.height,
            width,
            height,
            auto_x=self.position[0],
            auto_y=self.position[1],
            x_align=x_align,
            y_align=y_align
        )
        
        self.update_position(pos)
