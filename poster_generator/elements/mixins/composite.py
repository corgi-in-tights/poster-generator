from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from PIL import Image
from PIL import ImageDraw

MAX_ALPHA = 255
ALPHA_INDEX = 3

class CompositeElementMixin(ABC):
    def should_alpha_composite(self, color) -> bool:
        if isinstance(color, tuple) and len(color) == ALPHA_INDEX + 1:
            if color[ALPHA_INDEX] < MAX_ALPHA:
                return True
        return False

    @abstractmethod
    def get_composite_params(self) -> dict:
        """
        List of parameters required for alpha compositing.
        Returns:
            list:
                Each value in the returned list is a dictionary consisting of the
                kwargs passed to the composite function.
        """

    def draw(self, image_draw: ImageDraw.Draw, image: Image.Image, blend_settings: dict | None = None) -> None:
        opacity_modifier = (blend_settings or {}).get("opacity", 1.0)

        composite_params = self.get_composite_params()
        for params in composite_params:
            if opacity_modifier < 1.0 or params.get("has_alpha", True):
                self.apply_alpha_composites(image, params=params, opacity_modifier=opacity_modifier)
            else:
                self.draw_composite(image_draw, **params)

    @abstractmethod
    def draw_composite(
        self,
        image_draw: ImageDraw.Draw,
        image: Image.Image,
        **kwargs,
    ) -> None:
        """
        Draw the composite element onto the canvas.

        Args:
            image_draw: PIL ImageDraw instance for drawing operations.
            image: PIL Image instance representing the canvas.
            blend_settings: Dictionary containing blend settings (opacity, etc.).
        """

    def apply_alpha_composites(self, base_image, params=None, opacity_modifier=1.0):
        """
        Apply an overlay image with alpha channel onto a base image at the specified position.

        Args:
            base_image (PIL.Image): The base image to which the overlay will be applied.
            overlay_image (PIL.Image): The overlay image with alpha channel.
            position (tuple): (x, y) position where the overlay will be placed on the base image.
        """
        alpha_image = Image.new("RGBA", base_image.size, (255, 255, 255, 1-int(255 * opacity_modifier)))
        image_draw = ImageDraw.Draw(alpha_image, "RGBA")
        self.draw_composite(image_draw, base_image, **params)
        base_image.alpha_composite(alpha_image)
