from PIL import Image, ImageDraw

from .settings import get_logger

logger = get_logger()


class Canvas:
    def __init__(self, width=1080, height=1350, background="#fff", size=None):
        self.width = size[0] if size else width
        self.height = size[1] if size else height
        self.background = background
        self._construct()

    def _construct(self):
        self._layers = {}
        self._image = Image.new("RGB", (self.width, self.height), self.background)
        self._draw = ImageDraw.Draw(self._image)

    def clear(self, layer=None):
        if layer is not None:
            if layer in self._layers:
                del self._layers[layer]
        else:
            self._construct()

    def add_element(self, identifier, element, layer=0):
        if layer < 0 or not isinstance(layer, int):
            raise ValueError(f"Layer {layer} must be a non-negative integer.")
        self._ensure_uniqueness(identifier)

        if layer not in self._layers:
            self._layers[layer] = {}
        self._layers[layer][identifier] = element

    def _ensure_uniqueness(self, identifier):
        identifiers = set()
        for layer in self._layers.values():
            for identifier in layer.keys():
                if identifier in identifiers:
                    raise ValueError(
                        f"Duplicate element identifier found: '{identifier}'"
                    )
                identifiers.add(identifier)

    def get_element_by_identifier(self, identifier):
        for layer in self._layers.values():
            if identifier in layer:
                return layer[identifier]
        return None

    def get_all_elements(self):
        elements = []
        for layer in sorted(self._layers.keys()):
            elements.extend(self._layers[layer].values())
        return elements

    def render(self, global_op=None):
        for layer, elements in sorted(self._layers.items()):
            for k, e in elements.items():
                if e.is_ready():
                    if global_op is not None:
                        global_op(e)
                    e.draw(self._draw, self._image)
                else:
                    logger.warning(
                        f"Element '{k}' in layer {layer} is not ready and will be skipped."
                    )

            return self._image
