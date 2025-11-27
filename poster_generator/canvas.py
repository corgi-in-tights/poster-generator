import logging
import os

from PIL import Image
from PIL import ImageDraw


def setup_debug_logging():
    logger = logging.getLogger("poster_generator")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


IS_DEVELOPMENT = os.getenv("POSTER_GENERATOR_ENV") == "development"

logger = setup_debug_logging() if IS_DEVELOPMENT else logging.getLogger("poster_generator")


class Canvas:
    """
    A canvas for creating and managing poster elements with layers and groups.

    The Canvas class provides a flexible system for organizing drawable elements
    into layers and groups, with support for selective rendering and element queries.

    Args:
        width: Canvas width in pixels. Defaults to 1080.
        height: Canvas height in pixels. Defaults to 1350.
        background: Background color as hex string (e.g., "#fff"). Defaults to "#fff".

    Attributes:
        width: Canvas width in pixels.
        height: Canvas height in pixels.
        background: Background color.
        elements: Dictionary mapping element identifiers to element instances.
        layers: Dictionary of layers, each containing settings and element lists.
        groups: Dictionary of groups, each containing a set of element identifiers.
    """

    def __init__(self, width=1080, height=1350, background="#fff"):
        self.width = width
        self.height = height
        self.background = background
        self._construct()

    def _construct(self):
        # Identifier -> element instance map
        self.elements = {}
        # Fast ref for layers
        self.layers = {}
        # Fast ref for groups
        self.groups = {}

        self._image = Image.new("RGB", (self.width, self.height), self.background)
        self._draw = ImageDraw.Draw(self._image)

    def add_layer(self, layer_name, settings=None):
        """
        Add a new layer to the canvas.

        Args:
            layer_name: Name of the layer to add.
            settings: Optional dictionary of layer settings containing:
                - opacity: Float between 0.0 and 1.0 for layer opacity.
        """
        if layer_name not in self.layers:
            self.layers[layer_name] = {"settings": settings or {}, "elements": []}

    def add_element(self, identifier, element, groups=None, layer="default"):
        """
        Add an element to the canvas with optional layer and group membership.

        Args:
            identifier: Unique string identifier for the element.
            element: DrawableElement instance to add.
            groups: Optional list of group names this element belongs to.
            layer: Layer name to add the element to. Defaults to "default".

        Raises:
            ValueError: If an element with the same identifier already exists.
        """
        logger.debug("Adding element '%s' to layer '%s' and groups %s", identifier, layer, groups)

        if identifier in self.elements:
            msg = f"Element with identifier '{identifier}' already exists."
            raise ValueError(msg)

        if groups is None:
            groups = []

        # Add to element registry
        self.elements[identifier] = element

        # Add to layer
        if layer not in self.layers:
            self.layers[layer] = {"settings": {}, "elements": []}
        self.layers[layer]["elements"].append(identifier)

        # Add to groups (sets)
        for group in groups:
            if group not in self.groups:
                self.groups[group] = []
            self.groups[group].append(identifier)

        element.bind_canvas(self, identifier)

    def remove_element(self, identifier):
        """
        Remove a single element from the canvas.

        Args:
            identifier: The unique identifier of the element to remove.
        """
        self.remove_elements([identifier])

    def remove_elements(self, identifiers):
        """
        Remove multiple elements from the canvas registry and from all layers/groups.

        Args:
            identifiers: List of element identifiers to remove.
        """
        for identifier in identifiers:
            # Remove from element registry
            self.elements.pop(identifier, None)

            # Remove from all layers (lists, safe removal)
            for layer_info in self.layers.values():
                if identifier in layer_info["elements"]:
                    layer_info["elements"].remove(identifier)

            # Remove from all groups
            for element_ids in self.groups.values():
                if identifier in element_ids:
                    element_ids.remove(identifier)  # safe, no error

    def clear_layer(self, layer):
        """
        Remove all elements from a layer and delete the layer.

        Args:
            layer: Name of the layer to clear.
        """
        if layer in self.layers:
            identifiers = self.layers[layer]["elements"].copy()
            self.remove_elements(identifiers)
            del self.layers[layer]

    def clear_group(self, group):
        """
        Remove all elements from a group and delete the group.

        Args:
            group: Name of the group to clear.
        """
        if group in self.groups:
            identifiers = list(self.groups[group])  # copy
            self.remove_elements(identifiers)
            del self.groups[group]

    def get_first_element(self, identifier=None, groups=None, layers=None):
        elements = self.get_elements(
            identifiers=[identifier] if identifier is not None else None,
            groups=groups,
            layers=layers,
            require_all=True,
        )
        return elements[0] if elements else None

    def _norm_set(self, value):
        if value is None:
            return set()
        if isinstance(value, str):
            return {value}
        return set(value)

    def get_elements(
        self,
        *,
        identifiers=None,
        groups=None,
        layers=None,
        require_all=True,
    ):
        """
        Query and retrieve elements by identifiers, groups, or layers.

        Returns element instances matching the specified filters. By default, elements
        matching ANY condition are returned. Set require_all=True to return only elements
        matching ALL conditions.

        Args:
            identifiers: Single identifier (str) or list of identifiers to match.
            groups: Single group name (str) or list of group names to match.
            layers: Single layer name (str) or list of layer names to match.
            require_all: If True, elements must match ALL conditions. If False (default),
                        elements matching ANY condition are returned.

        Returns:
            List of DrawableElement instances matching the query criteria.
        """
        logger.debug(
            "Querying elements with identifiers=%s, groups=%s, layers=%s, require_all=%s",
            identifiers,
            groups,
            layers,
            require_all,
        )

        id_filter = self._norm_set(identifiers)
        group_filter = self._norm_set(groups)
        layer_filter = self._norm_set(layers)

        if not id_filter and not group_filter and not layer_filter:
            return list(self.elements.values())

        group_hits = set()
        for g in group_filter:
            group_hits |= set(self.groups.get(g, []))

        layer_hits = set()
        for lf in layer_filter:
            layer_hits |= set(self.layers.get(lf, {}).get("elements", []))

        results = []
        for ident, elem in self.elements.items():
            match_ident = (not id_filter) or (ident in id_filter)
            match_group = (not group_filter) or (ident in group_hits)
            match_layer = (not layer_filter) or (ident in layer_hits)

            matches = (match_ident, match_group, match_layer)

            if (require_all and all(matches)) or (not require_all and any(matches)):
                results.append(elem)

        logger.debug("Found %d matching elements", len(results))

        return results

    def crop(self, x1: float, y1: float, x2: float, y2: float):
        """
        Crop the canvas image to the specified box.

        WARNING: This is a destructive operation that modifies the canvas size
        and removes any elements outside the crop region.

        Args:
            x1: Left coordinate of the crop box.
            y1: Top coordinate of the crop box.
            x2: Right coordinate of the crop box.
            y2: Bottom coordinate of the crop box.
        """
        box = (x1, y1, x2, y2)
        self._image = self._image.crop(box)
        self.width, self.height = self._image.size
        self._draw = ImageDraw.Draw(self._image)

        # remove elements that are out of bounds
        to_remove = []
        for identifier, element in self.elements.items():
            if not element.overlaps_region(x1, y1, x2, y2):
                to_remove.append(identifier)
        self.remove_elements(to_remove)

    def render(self, global_op=None):
        """
        Render all layers and elements to create the final image.

        Args:
            global_op: Optional callable to apply to each element before rendering.
                      Should accept an element instance as its argument.

        Returns:
            PIL.Image.Image: The rendered image.
        """
        for layer_name, layer_info in self.layers.items():
            self._render_layer(layer_name, layer_info, global_op)
        return self._image

    def _render_layer(self, layer_name, layer_info, global_op=None):
        layer_settings = layer_info["settings"]
        opacity = layer_settings.get("opacity", 1.0)

        for identifier in layer_info["elements"]:
            e = self.elements.get(identifier)
            if e is None:
                logger.warning("Element '%s' listed in layer %s not found in registry.", identifier, layer_name)
                continue

            if e.is_ready():
                if global_op is not None:
                    global_op(e)

                logger.debug("CANVAS: Drawing element '%s' in layer '%s'", identifier, layer_name)
                e.draw(self._draw, self._image, blend_settings={"opacity": opacity})
            else:
                logger.warning("Element '%s' in layer %s is not ready and will be skipped.", identifier, layer_name)

    @staticmethod
    def from_dict(data: dict) -> "Canvas":
        """
        Create a Canvas instance from a dictionary configuration.

        Args:
            data: Dictionary containing canvas settings with optional keys:
                - width: Canvas width in pixels (default: 1080)
                - height: Canvas height in pixels (default: 1350)
                - background: Background color as hex string (default: "#fff")

        Returns:
            Canvas: A new Canvas instance configured with the provided settings.
        """
        width = data.get("width", 1080)
        height = data.get("height", 1350)
        background = data.get("background", "#fff")

        return Canvas(width=width, height=height, background=background)
