from __future__ import annotations

import copy
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from poster_generator.utils import get_alignment_position

if TYPE_CHECKING:
    from PIL import Image, ImageDraw

    from poster_generator.canvas import Canvas

logger = logging.getLogger(__name__)


class DrawableElement(ABC):
    """Abstract base class for all drawable elements in a poster.

    This class defines the interface for all drawable elements that can be positioned
    and rendered on an image. Subclasses must implement methods for drawing, checking
    readiness, detecting overlaps, and applying operations.

    Attributes:
        position (tuple): The (x, y) coordinates of the element on the canvas, defaults to (0, 0).
    """

    def __init__(self, position=(0, 0)):
        """Initialize a DrawableElement with a position.

        Args:
            position (tuple): The (x, y) coordinates of the element on the canvas, defaults to (0, 0).
        """
        if position is None:
            self.position = (0, 0)
        else:
            self.position = (int(position[0]), int(position[1]))

    def bind_canvas(self, canvas: Canvas, identifier: str):
        """
        Bind the drawable element to a specific canvas. This should be called when
        the element is added to the canvas.

        NOTE: This method breaks the previous connected canvas-element relationship if called multiple
        times with different canvases and the values should only be used when absolutely necessary or for debugging.

        Args:
            canvas (Canvas): The canvas to bind the element to.
            identifier (str): The unique identifier of the element within the canvas.
        """
        self._identifier = identifier
        self._canvas = canvas

    @abstractmethod
    def draw(self, image_draw: ImageDraw.Draw, image: Image.Image, blend_settings: dict | None = None) -> None:
        """
        Draw the element onto the image.

        This method must be implemented by all subclasses to define how the element
        should be rendered onto the image.

        Args:
            image_draw (ImageDraw.Draw): The ImageDraw object used for drawing operations.
            image (Image.Image): The PIL Image object to draw on.
            blend_settings (dict | None, optional): Dictionary containing blending settings
                for the drawing operation. Defaults to None.
        """

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if the drawable element is ready to be rendered.

        Returns:
            bool: True if the element is ready for rendering, otherwise False.
        """

    @abstractmethod
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """
        Check if this drawable overlaps with a rectangular region.

        Args:
            x1 (float): The x-coordinate of the top-left corner of the region.
            y1 (float): The y-coordinate of the top-left corner of the region.
            x2 (float): The x-coordinate of the bottom-right corner of the region.
            y2 (float): The y-coordinate of the bottom-right corner of the region.

        Returns:
            bool: True if the drawable overlaps with the region, otherwise False.
        """

    def overlaps_at(self, x: float, y: float) -> bool:
        """
        Check if this drawable overlaps with a point at the given coordinates.

        Args:
            x (float): The x-coordinate of the point to check.
            y (float): The y-coordinate of the point to check.

        Returns:
            bool: True if the drawable overlaps with the point, otherwise False.

        Note:
            This method uses a small epsilon value (1e-5) to create a tiny region
            around the point and checks if the drawable overlaps with that region.
        """
        eps = 1e-5
        return self.overlaps_region(x, y, x + eps, y + eps)

    def apply_operation(self, operation, kwargs):
        """
        Apply a transformation operation to the drawable element.

        Args:
            operation: Callable that takes a DrawableElement and modifies it.
        """
        operation(self, **kwargs)

    @abstractmethod
    def get_size(self):
        """
        Return the pixel width/height of the drawable element.

        Returns:
            (width, height): Tuple of width and height in pixels.
        """

    def update_position(self, position):
        """
        Update the position of the drawable element.

        Args:
            position: New position to set for the drawable element.
        """
        logger.debug("Updating position from %s to %s", self.position, position)
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

    def align_to(
        self,
        x_align: float | None = None,
        y_align: float | None = None,
        parent_element: DrawableElement | str | None = None,
        canvas=None,
    ):
        """
        In-place position update on this element relative to a parent element or canvas.

        Args:
            x_align (float | None, optional): Horizontal alignment value between 0.0 (left) and 1.0 (right).
                If None, the current x position is maintained. Defaults to None.
            y_align (float | None, optional): Vertical alignment value between 0.0 (top) and 1.0 (bottom).
                If None, the current y position is maintained. Defaults to None.
            parent_element (DrawableElement | str | None, optional): The parent element to align to.
                Can be a DrawableElement instance, a string identifier to look up the element,
                or None to align to the canvas. Defaults to None.
            canvas (optional): The canvas context to use for element lookups. If None, uses
                the element's internal canvas reference. Defaults to None.

        Raises:
            ValueError: If parent_element is a string identifier that cannot be found in the bound canvas.
        """
        canvas = canvas or self._canvas
        if isinstance(parent_element, str):
            parent_element = canvas.get_first_element(identifier=parent_element)
            if parent_element is None:
                msg = f"Parent element '{parent_element}' not found for alignment."
                raise ValueError(msg)

        pos = get_alignment_position(
            element_size=self.get_size(),
            parent_size=parent_element.get_size() if parent_element else (self._canvas.width, self._canvas.height),
            x_align=x_align,
            y_align=y_align,
            parent_position=parent_element.position if parent_element else (0, 0),
            original_position=self.position,
        )
        self.update_position(pos)

    def copy(self):
        """
        Create a copy of the drawable element.

        Returns:
            DrawableElement: A new instance that is a copy of this element.
        """
        return copy.deepcopy(self)

    def apply_opacity_modifier(self, color: tuple, opacity_modifier: float):
        """
        Helper to apply an opacity modifier to an RGBA color tuple.

        Args:
            color (tuple): The original RGBA color tuple.
            opacity_modifier (float): The opacity modifier to apply (between 0.0 and 1.0).

        Returns:
            tuple: The modified RGBA color tuple with adjusted alpha.
        """
        if color is not None:
            r, g, b, a = color
            a = int(a * opacity_modifier)
            return (r, g, b, a)
        return color
