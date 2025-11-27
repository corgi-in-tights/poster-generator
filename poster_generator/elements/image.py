from pathlib import Path

from PIL import Image

from .drawable import DrawableElement


class ImageElement(DrawableElement):
    """A drawable element that represents an image on the poster canvas.

    This class handles loading, resizing, and rendering images onto the poster with support
    for alpha blending and various image transformations through operations.

    Attributes:
        image_path (str): Path to the image file.
        width (int): The width of the image in pixels.
        height (int): The height of the image in pixels.
        image (PIL.Image.Image or None): The loaded PIL Image object in RGBA mode.

    Example:
        >>> img_element = ImageElement(
        ...     position=(100, 100),
        ...     image_path="path/to/image.png",
        ...     width=500,
        ...     height=300
        ... )
        >>> img_element.is_ready()
        True
    """

    def __init__(self, image_path=None, position=(0, 0), width=None, height=None):
        """Initialize an ImageElement with position and optional dimensions.

        Args:
            position (tuple): The (x, y) coordinates of the image's top-left corner.
            image_path (str): Path to the image file to be loaded.
            width (int, optional): The desired width of the image. If None, uses original width. Defaults to None.
            height (int, optional): The desired height of the image. If None, uses original height. Defaults to None.
        """
        super().__init__(position)
        self.width = width
        self.height = height
        self.image = None

        if image_path is not None:
            self.load_image(image_path)


    def resize_image(self, new_width, new_height):
        self.image = self.image.resize((new_width, new_height))
        self.width = new_width
        self.height = new_height

    def set_image(self, new_image):
        self.image = new_image.convert("RGBA")
        # Set from image for any missing attributes
        if self.width is None:
            self.width = self.image.width
        if self.height is None:
            self.height = self.image.height

        self.resize_image(self.width, self.height)

    def set_image_path(self, new_path):
        if Path(new_path).is_file():
            self.set_image(Image.open(new_path))
        else:
            msg = f"Image path '{new_path}' is invalid or does not exist."
            raise ValueError(msg)


    def draw(self, draw_ctx, canvas_image, blend_settings: dict | None = None):
        """
        Draw the image onto the canvas with alpha blending.

        Args:
            draw_ctx: PIL ImageDraw instance (not used for image drawing).
            canvas_image: PIL Image instance representing the canvas.
            blend_settings: Dictionary containing blend settings (opacity, etc.).

        Raises:
            ValueError: If no position is specified or no image is loaded.
        """
        if self.position is None:
            msg = "No position specified for ImageElement drawing."
            raise ValueError(msg)

        pos2 = (
            self.position[0] + self.width if self.width else 0,
            self.position[1] + self.height if self.height else 0,
        )

        if self.image is None:
            msg = "No image loaded to draw."
            raise ValueError(msg)

        out = self.image.split()
        canvas_image.paste(self.image, (*self.position, *pos2), out[3])

    def is_ready(self):
        """
        Check if the image element is ready to be drawn.

        Returns:
            bool: True if an image is loaded.
        """
        return self.image is not None

    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        return (
            self.position[0] <= x1 <= self.position[0] + (self.width or 0)
            and self.position[1] <= y1 <= self.position[1] + (self.height or 0)
            and self.position[0] <= x2 <= self.position[0] + (self.width or 0)
            and self.position[1] <= y2 <= self.position[1] + (self.height or 0)
        )

    def get_size(self):
        """
        Return the pixel width/height of the image element.

        Returns:
            (width, height): Tuple of width and height in pixels.
        """
        return (self.width or 0, self.height or 0)
