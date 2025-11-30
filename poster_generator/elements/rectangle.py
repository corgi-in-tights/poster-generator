"""Rectangle element implementation for rendering filled rectangles on canvas."""

from .abstract import ShapeElement


class RectangleElement(ShapeElement):
    """A drawable rectangle element with support for rounded corners and styling.

    The rectangle is positioned by its top-left corner and can have rounded corners
    specified by a radius parameter. Supports both fill and outline colors.

    Attributes:
        border_radius (int): Corner radius in pixels for rounded corners (0 for sharp corners).

    Example:
        >>> rect = RectangleElement(
        ...     position=(100, 100),
        ...     width=300,
        ...     height=200,
        ...     fill=(1.0, 0.34, 0.2, 1.0)
        ... )
        >>>
        >>> rounded_rect = RectangleElement(
        ...     position=(100, 100),
        ...     width=300,
        ...     height=200,
        ...     fill="#3498db",
        ...     outline="#2c3e50",
        ...     outline_width=3,
        ...     border_radius=20
        ... )
    """

    def __init__(
        self,
        *,
        border_radius=0,
        other_position=None,
        **kwargs,
    ):
        """
        Initialize a Rectangle element.

        Args:
            border_radius (int, optional): The radius of the rectangle's corners. Defaults to 0.
            other_position (tuple, optional): An alternative position (x, y) to calculate width and height
                from the base position. If provided, width and height are computed as the absolute difference
                between other_position and self.position. Defaults to None.
            **kwargs: Additional keyword arguments passed to the ShapeElement constructor.
        """
        super().__init__(**kwargs)
        if other_position is not None:
            self.width = abs(other_position[0] - self.position[0])
            self.height = abs(other_position[1] - self.position[1])
        self.border_radius = border_radius

    def draw_composite(self, image_draw, image, **kwargs):
        x, y = self.position
        x2, y2 = x + self.width, y + self.height

        fill = kwargs.get("fill", self.fill)
        outline = kwargs.get("outline", self.outline)
        outline_width = kwargs.get("outline_width", self.outline_width)

        if self.border_radius > 0:
            image_draw.rounded_rectangle(
                [(x, y), (x2, y2)],
                radius=self.border_radius,
                fill=fill,
                outline=outline,
                width=outline_width,
            )
        else:  # Draw regular rectangle
            image_draw.rectangle(
                [(x, y), (x2, y2)],
                fill=fill,
                outline=outline,
                width=outline_width,
            )

    def is_ready(self) -> bool:
        """
        Check if the rectangle element is ready to be drawn.

        Returns:
            bool: True if position, width, and height are set.
        """
        return self.position is not None and self.width is not None and self.height is not None
