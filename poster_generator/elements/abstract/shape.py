from __future__ import annotations

from abc import ABC

from poster_generator.elements.mixins import CompositeElementMixin
from poster_generator.utils import normalize_color

from .drawable import DrawableElement


class ShapeElement(CompositeElementMixin, DrawableElement, ABC):
    """Abstract base class for drawable shape elements with fill and outline styling.

    This class extends DrawableElement to provide common functionality for shape-based
    elements such as rectangles and ellipses. It includes support for fill colors,
    outline colors, and alpha compositing for transparency effects.

    Attributes:
        width (int | None): Width of the shape in pixels.
        height (int | None): Height of the shape in pixels.
        fill (tuple | None): Fill color as normalized RGBA tuple (r, g, b, a).
        outline (tuple | None): Outline color as normalized RGBA tuple (r, g, b, a).
        outline_width (int): Width of the outline in pixels, defaults to 1.
    """

    def __init__(
        self,
        *,
        width=None,
        height=None,
        fill=None,
        outline=None,
        outline_width=1,
        **kwargs,
    ):
        """Initialize a ShapeElement with dimensions and styling.

        Args:
            width (int): Width of the shape in pixels. Defaults to None.
            height (int): Height of the shape in pixels. Defaults to None.
            fill (str | list | dict | None): Fill color as hex string, RGBA list,
                or RGBA dict. Defaults to None.
            outline (str | list | dict | None): Outline color as hex string, RGBA list,
                or RGBA dict. Defaults to None.
            outline_width (int): Width of the outline in pixels. Defaults to 1.
            **kwargs: Additional keyword arguments passed to the DrawableElement constructor.
        """
        super().__init__(**kwargs)
        self.width = int(width) if width is not None else None
        self.height = int(height) if height is not None else None
        self.fill = normalize_color(fill)
        self.outline = normalize_color(outline)
        self.outline_width = outline_width

    def get_composite_params(self, opacity_modifier=1.0) -> list[dict]:
        """Generate composite parameters for rendering the shape with alpha blending.

        This method determines how to render the shape based on whether the fill and
        outline colors have alpha transparency. When alpha is present, separate render
        passes are created for fill and outline to ensure proper compositing.

        Args:
            opacity_modifier (float, optional): Additional opacity multiplier to apply
                to the shape's colors (0.0 to 1.0). Defaults to 1.0.

        Returns:
            list[dict]: List of parameter dictionaries for each render pass. Each dict contains:
                - fill (tuple | None): RGBA color for fill or None
                - outline (tuple | None): RGBA color for outline or None
                - outline_width (int): Width of outline in pixels
                - has_alpha (bool): Whether this pass requires alpha compositing
        """
        params = []
        should_alpha_fill = self.fill and self.should_alpha_composite(self.fill)
        should_alpha_outline = self.should_alpha_composite(self.outline)

        if not should_alpha_fill and not should_alpha_outline:
            params.append(
                {
                    "has_alpha": False,
                    "fill": self.apply_opacity_modifier(self.fill, opacity_modifier),
                    "outline": self.apply_opacity_modifier(self.outline, opacity_modifier),
                    "outline_width": self.outline_width,
                },
            )
        else:
            if self.fill:
                params.append(
                    {
                        "fill": self.fill,
                        "outline": None,
                        "outline_width": 0,
                        "has_alpha": should_alpha_fill,
                    },
                )

            if self.outline and self.outline_width > 0:
                params.append(
                    {
                        "fill": None,
                        "outline": self.outline,
                        "outline_width": self.outline_width,
                        "has_alpha": should_alpha_outline,
                    },
                )

        return params

    def get_size(self):
        """Return the dimensions of the shape element.

        Returns:
            tuple: (width, height) in pixels.
        """
        return self.width, self.height

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Check if this shape overlaps with a rectangular region.

        Uses a bounding box approach to determine if the shape's rectangular bounds
        overlap with the specified region.

        Args:
            x1 (float): Left edge of the query region.
            y1 (float): Top edge of the query region.
            x2 (float): Right edge of the query region.
            y2 (float): Bottom edge of the query region.

        Returns:
            bool: True if the shape overlaps with the specified region, otherwise False.
        """
        if self.position is None:
            return False

        rect_x1, rect_y1 = self.position
        rect_x2 = rect_x1 + self.width
        rect_y2 = rect_y1 + self.height

        return not (
            rect_x2 < x1  # Rectangle is to the left of region
            or rect_x1 > x2  # Rectangle is to the right of region
            or rect_y2 < y1  # Rectangle is above region
            or rect_y1 > y2  # Rectangle is below region
        )

    def is_ready(self) -> bool:
        """Check if the shape element is ready to be drawn.

        Returns:
            bool: True if position, width, and height are all set, otherwise False.
        """
        return self.position is not None and self.width is not None and self.height is not None
