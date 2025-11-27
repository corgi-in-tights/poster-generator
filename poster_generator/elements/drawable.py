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
    
    def __init__(self, position=(0, 0)):
        """Initialize a DrawableElement with a position.
        
        Args:
            position (tuple): The (x, y) coordinates for the element.
        """
        if position is None:
            position = (0, 0)
        self.position = position
    
    def bind_canvas(self, canvas: "Canvas", identifier: str):
        """
        Bind the drawable element to a specific canvas. This should be called when
        the element is added to the canvas.
        
        NOTE: This method breaks the previous connected canvas-element relationship
        if called multiple times with different canvases and the values should only 
        be used when absolutely necessary.

        Args:
            canvas (Canvas): The canvas to bind the element to.
            identifier (str): The unique identifier of the element within the canvas.
        """
        self._identifier = identifier
        self._canvas = canvas
    
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

    def apply_operation(self, operation, params):
        """
        Apply a transformation operation to the drawable element.
        
        Args:
            operation: Callable that takes a DrawableElement and modifies it.
        """
        operation(self, **params)
    
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
        self.update_position((self.position[0] + dx, self.position[1] + dy))
        
    def align_to(self, canvas: "Canvas", parent_element_id: str = None, x_align: str = "auto", y_align: str = "auto"):        
        pos = get_alignment_position(
            canvas,
            parent_element_id=parent_element_id,
            x_align=x_align,
            y_align=y_align
        )
        self.update_position(pos)

    def get_alignment_position(self, canvas: "Canvas", parent_element_id: str = None, x_align: float = None, y_align: float = None):
        
        width, height = self.get_size()
        
        if parent_element_id is None:
            parent_width, parent_height = canvas.width, canvas.height
            parent_x, parent_y = 0, 0
        else:
            parent_element = canvas.get_first_element(identifier=parent_element_id)
            if parent_element is None:
                msg = f"Parent element '{parent_element_id}' not found for alignment."
                raise ValueError(msg)
            
            parent_width, parent_height = parent_element.get_size()
            parent_x, parent_y = parent_element.position
        
        pos = get_alignment_position(
            parent_width,
            parent_height,
            width,
            height,
            parent_x=parent_x,
            parent_y=parent_y,
            auto_x=self.position[0],
            auto_y=self.position[1],
            x_align=x_align,
            y_align=y_align
        )
        
        return pos

    def copy(self):
        """
        Create a copy of the drawable element.

        Returns:
            DrawableElement: A new instance that is a copy of this element.
        """
        import copy
        return copy.deepcopy(self)