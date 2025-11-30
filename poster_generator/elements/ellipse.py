"""Ellipse element implementation for rendering filled ellipses on canvas."""

from .abstract import ShapeElement


class EllipseElement(ShapeElement):
    """A drawable ellipse element with support for fill and outline colors.

    The ellipse is positioned by its top-left corner and sized by width and height.

    Example:
        >>> # Simple filled ellipse
        >>> ellipse = EllipseElement(
        ...     position=(100, 100),
        ...     width=150,
        ...     height=100,
        ...     fill="#3498db"
        ... )
        >>>
        >>> # Ellipse with outline
        >>> outlined_ellipse = EllipseElement(
        ...     position=(100, 100),
        ...     width=150,
        ...     height=100,
        ...     fill="#e74c3c",
        ...     outline="#c0392b",
        ...     outline_width=3
        ... )
    """

    def draw_composite(self, image_draw, image, **kwargs):
        x, y = self.position

        fill = kwargs.get("fill", self.fill)
        outline = kwargs.get("outline", self.outline)
        outline_width = kwargs.get("outline_width", self.outline_width)

        # Calculate bounding box for the ellipse
        x1, y1 = x, y
        x2, y2 = x + self.width, y + self.height

        image_draw.ellipse(
            [(x1, y1), (x2, y2)],
            fill=fill,
            outline=outline,
            width=outline_width,
        )

    def overlaps_point(self, x: float, y: float) -> bool:
        """
        Check if a point is inside the ellipse.

        Uses the ellipse equation to check if a point is within the ellipse.

        Args:
            x: X coordinate of the point.
            y: Y coordinate of the point.

        Returns:
            bool: True if the point is inside or on the ellipse.
        """
        if self.position is None:
            return False

        ellipse_x, ellipse_y = self.position

        # Calculate center of ellipse
        center_x = ellipse_x + self.width / 2
        center_y = ellipse_y + self.height / 2

        # Semi-axes
        a = self.width / 2
        b = self.height / 2

        # Ellipse equation: ((x - cx) / a)^2 + ((y - cy) / b)^2 <= 1
        if a == 0 or b == 0:
            return False

        result = ((x - center_x) / a) ** 2 + ((y - center_y) / b) ** 2
        return result <= 1
