from __future__ import annotations

from abc import ABC

from poster_generator.elements.mixins import CompositeElementMixin
from poster_generator.utils import normalize_color

from .drawable import DrawableElement


class ShapeElement(CompositeElementMixin, DrawableElement, ABC):
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
        super().__init__(**kwargs)
        self.width = int(width) if width is not None else None
        self.height = int(height) if height is not None else None
        self.fill = normalize_color(fill)
        self.outline = normalize_color(outline)
        self.outline_width = outline_width

    def get_composite_params(self, opacity_modifier=1.0) -> list[dict]:
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
        return self.width, self.height

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
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
        """
        Check if the ellipse element is ready to be drawn.

        Returns:
            bool: True if position, width, and height are set.
        """
        return self.position is not None and self.width is not None and self.height is not None
