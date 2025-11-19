from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image, ImageDraw
    
class DrawableElement(ABC):
    """
    Abstract base class for drawable elements in a poster.
    This class defines the interface for all drawable elements that can be positioned
    and rendered on an image. Subclasses must implement methods for drawing, checking
    readiness, detecting overlaps, and applying operations.
    Attributes:
        position: The position of the drawable element on the canvas.
    Methods:
        draw(image_draw, image, position=None, opacity=1.0):
            Renders the element onto the provided image.
        is_ready():
            Checks if the element is ready to be drawn.
        overlaps_region(x1, y1, x2, y2):
            Determines if the element overlaps with a rectangular region.
        overlaps_at(x, y):
            Determines if the element overlaps with a specific point.
        apply_operation(operation):
            Applies a transformation or operation to the element.
    """
    def __init__(self, position):
        self.position = position
    
    @abstractmethod
    def draw(self, image_draw: "ImageDraw.Draw", image: "Image.Image", position=None, opacity=1.0) -> None:
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
        