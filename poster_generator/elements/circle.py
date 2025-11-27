"""Circle element implementation for rendering filled circles on canvas."""

from typing import TYPE_CHECKING

from .drawable import DrawableElement

if TYPE_CHECKING:
    from PIL import Image
    from PIL import ImageDraw


class CircleElement(DrawableElement):
    """A drawable circle element with support for background and outline colors.

    The circle is positioned by its center point and sized by its radius.
    Supports both background and outline styling.

    Attributes:
        radius (int): Circle radius in pixels.
        background (str): background color as hex string (e.g., "#FF5733").
        outline_color (str or None): Outline color as hex string, or None for no outline.
        outline_width (int): Width of the outline in pixels.

    Example:
        >>> # Simple filled circle
        >>> circle = CircleElement(
        ...     position=(200, 200),
        ...     radius=75,
        ...     background="#3498db"
        ... )
        >>>
        >>> # Circle with outline
        >>> outlined_circle = CircleElement(
        ...     position=(200, 200),
        ...     radius=75,
        ...     background="#e74c3c",
        ...     outline_color="#c0392b",
        ...     outline_width=3
        ... )
    """

    def __init__(self, position=(0, 0), radius=50, background="#000000", outline_color=None, outline_width=1):
        """Initialize a CircleElement with specified radius and styling.

        Args:
            position (tuple): The (x, y) coordinates for the center of the circle.
            radius (int, optional): Radius of the circle in pixels. Defaults to 50.
            background (str, optional): background color as hex string. Defaults to "#000000".
            outline_color (str, optional): Outline color as hex string. Defaults to None (no outline).
            outline_width (int, optional): Width of the outline in pixels. Defaults to 1.
        """
        super().__init__(position=position)
        self.radius = radius
        self.background = background
        self.outline_color = outline_color
        self.outline_width = outline_width

    def draw(self, image_draw: "ImageDraw.Draw", image: "Image.Image", blend_settings: dict) -> None:
        """
        Draw the circle onto the canvas.

        Args:
            image_draw: PIL ImageDraw instance for drawing operations.
            image: PIL Image instance representing the canvas (not used for circles).
            blend_settings: Dictionary containing blend settings (opacity, etc.).

        Raises:
            ValueError: If position is not set.
        """
        center_x, center_y = self.position

        # Calculate bounding box for the circle
        x1 = center_x - self.radius
        y1 = center_y - self.radius
        x2 = center_x + self.radius
        y2 = center_y + self.radius

        # Draw the circle (ellipse with equal width and height)
        image_draw.ellipse(
            [(x1, y1), (x2, y2)], fill=self.background, outline=self.outline_color, width=self.outline_width,
        )

    def is_ready(self) -> bool:
        """
        Check if the circle element is ready to be drawn.

        Returns:
            bool: True if position and radius are set.
        """
        return self.position is not None and self.radius is not None

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """
        Check if this circle overlaps with a rectangular region.

        Uses a simplified bounding box approach to check if the circle's
        bounding box overlaps with the specified region.

        Args:
            x1: Left edge of the query region.
            y1: Top edge of the query region.
            x2: Right edge of the query region.
            y2: Bottom edge of the query region.

        Returns:
            bool: True if the circle overlaps with the specified region.
        """
        if self.position is None:
            return False

        center_x, center_y = self.position

        # Circle's bounding box
        circle_x1 = center_x - self.radius
        circle_y1 = center_y - self.radius
        circle_x2 = center_x + self.radius
        circle_y2 = center_y + self.radius

        # Check if bounding boxes overlap
        return not (
            circle_x2 < x1  # Circle is to the left of region
            or circle_x1 > x2  # Circle is to the right of region
            or circle_y2 < y1  # Circle is above region
            or circle_y1 > y2  # Circle is below region
        )

    def overlaps_point(self, x: float, y: float) -> bool:
        """
        Check if a point is inside the circle.

        Uses the distance formula to check if a point is within the circle's radius.

        Args:
            x: X coordinate of the point.
            y: Y coordinate of the point.

        Returns:
            bool: True if the point is inside or on the circle.
        """
        if self.position is None:
            return False

        center_x, center_y = self.position

        # Calculate distance from center to point
        distance_squared = (x - center_x) ** 2 + (y - center_y) ** 2
        radius_squared = self.radius**2

        return distance_squared <= radius_squared

    def get_size(self):
        """
        Get the dimensions of the circle's bounding box.

        Returns:
            tuple: (width, height) of the bounding box (both equal to diameter).
        """
        diameter = self.radius * 2
        return (diameter, diameter)
