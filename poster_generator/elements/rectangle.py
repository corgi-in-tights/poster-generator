"""Rectangle element implementation for rendering filled rectangles on canvas."""


from .abstract import ShapeElement


class RectangleElement(ShapeElement):
    """A drawable rectangle element with support for rounded corners and styling.

    The rectangle is positioned by its top-left corner and can have rounded corners
    specified by a radius parameter. Supports both fill and outline colors.

    Attributes:
        width (int): Rectangle width in pixels.
        height (int): Rectangle height in pixels.
        fill (str): Fill color as hex string (e.g., "#FF5733").
        outline (str or None): Outline color as hex string, or None for no outline.
        outline_width (int): Width of the outline in pixels.
        radius (int): Corner radius in pixels for rounded corners (0 for sharp corners).

    Example:
        >>> rect = RectangleElement(
        ...     position=(100, 100),
        ...     width=300,
        ...     height=200,
        ...     fill="#FF5733"
        ... )
        >>>
        >>> rounded_rect = RectangleElement(
        ...     position=(100, 100),
        ...     width=300,
        ...     height=200,
        ...     fill="#3498db",
        ...     outline="#2c3e50",
        ...     outline_width=3,
        ...     radius=20
        ... )
    """

    def __init__(
        self,
        *,
        border_radius=0,
        other_position=None,
        **kwargs,
    ):
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
                [(x, y), (x2, y2)], fill=fill, outline=outline, width=outline_width,
            )

    def is_ready(self) -> bool:
        """
        Check if the rectangle element is ready to be drawn.

        Returns:
            bool: True if position, width, and height are set.
        """
        return self.position is not None and self.width is not None and self.height is not None


