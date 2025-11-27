from typing import Any

from .circle import CircleElement
from .drawable import DrawableElement
from .image import ImageElement
from .rectangle import RectangleElement
from .text import TextElement


class ElementFactory:
    def __init__(self):
        self._registry: dict[str, type[DrawableElement]] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register("text", TextElement)
        self.register("image", ImageElement)
        self.register("rectangle", RectangleElement)
        self.register("circle", CircleElement)

    def register(self, element_type: str, element_class: dict[DrawableElement]):
        """
        Register a new element type with the factory.

        Args:
            element_type: String identifier for the element type (e.g., "text", "image")
            element_class: The class to instantiate for this type
        """
        self._registry[element_type] = element_class

    def create_element(
        self, element_type: str, position: tuple[int, int] = (0, 0), values: dict[str, Any] | None = None, **kwargs,
    ) -> DrawableElement:
        """
        Create an element instance based on type.

        Args:
            element_type: The type of element to create (e.g., "text", "image")
            position: Optional (x, y) tuple for element position
            values: Dictionary of element-specific parameters
            **kwargs: Additional keyword arguments passed to the element constructor

        Returns:
            An instance of the requested DrawableElement subclass

        Raises:
            ValueError: If the element_type is not registered
        """
        if element_type not in self._registry:
            msg = f"Unknown element type '{element_type}'. Available types: {', '.join(self._registry.keys())}"
            raise ValueError(msg)

        element_class = self._registry[element_type]
        return element_class(position=position, **values)

    def get_registered_types(self) -> list[str]:
        """Return a list of all registered element types."""
        return list(self._registry.keys())

    def is_registered(self, element_type: str) -> bool:
        """Check if an element type is registered."""
        return element_type in self._registry


_default_factory = ElementFactory()


def get_factory() -> ElementFactory:
    """Get the default factory instance."""
    return _default_factory


def register_element(element_type: str, element_class: type[DrawableElement]):
    """
    Register a new element type in the global factory.

    Args:
        element_type: String identifier for the element type (e.g., "text", "image")
        element_class: The class to instantiate for this type
    """
    get_factory().register(element_type, element_class)
