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
        self.layers = {}
        self.groups = {}

        self._image = Image.new("RGB", (self.width, self.height), self.background)
        self._draw = ImageDraw.Draw(self._image)
            
    def clear_layer(self, layer):
        if layer in self.layers:
            self.remove_elements_from_groups(*self.layers[layer].keys())
            del self.layers[layer]
            
    def clear_group(self, group):
        if group in self.groups:
            identifiers = list(self.groups[group].keys())
            
            for identifier in identifiers:
                self.remove_elements(identifier)
                
            del self.groups[group]
            
    def remove_elements(self, *identifiers):
        # iterate layers to find and remove element
        for layer in self.layers.values():
            for identifier in identifiers:
                if identifier in layer:
                    del layer[identifier]
        self.remove_elements_from_groups(*identifiers)
        
    def remove_elements_from_groups(self, *identifiers):
        for identifier in identifiers:
            for group_elements in self.groups.values():
                if identifier in group_elements:
                    group_elements.remove(identifier)

    def add_element(self, identifier, element, group="default", layer=0):
        if layer < 0 or not isinstance(layer, int):
            raise ValueError(f"Layer {layer} must be a non-negative integer.")
        self._ensure_uniqueness(identifier)

        if layer not in self.layers:
            self.layers[layer] = {}
        self.layers[layer][identifier] = element

        if group not in self.groups:
            self.groups[group] = {}
        self.groups[group][identifier] = element

    def _ensure_uniqueness(self, identifier):
        identifiers = set()
        for layer in self.layers.values():
            for identifier in layer.keys():
                if identifier in identifiers:
                    raise ValueError(
                        f"Duplicate element identifier found: '{identifier}'"
                    )
                identifiers.add(identifier)

    def get_element_by_identifier(self, identifier):
        for layer in self.layers.values():
            if identifier in layer:
                return layer[identifier]
        return None

    def get_elements_by_group(self, group):
        elements = []
        if group in self.groups:
            return list(self.groups[group])
        return elements

    def get_all_elements(self):
        elements = []
        for layer in sorted(self.layers.keys()):
            elements.extend(self.layers[layer].values())
        return elements

    def render(self, global_op=None):
        for layer, elements in sorted(self.layers.items()):
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

