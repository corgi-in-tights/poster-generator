from PIL import Image, ImageDraw

from .settings import get_logger
from .elements.factory import get_factory
from .operations.factory import get_operation_factory

logger = get_logger()


class Canvas:
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

    def add_element(self, identifier, element, groups=None, layer="default"):
        logger.debug(f"CANVAS: Adding element '{identifier}' to layer '{layer}' and groups {groups}")
        
        if identifier in self.elements:
            raise ValueError(f"Element with identifier '{identifier}' already exists.")

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
                self.groups[group] = set()
            self.groups[group].add(identifier)

    def remove_element(self, identifier):
        self.remove_elements([identifier])

    def remove_elements(self, identifiers):
        """Remove multiple elements from registry + all indexes."""
        for identifier in identifiers:
            # Remove from element registry
            self.elements.pop(identifier, None)

            # Remove from all layers (lists, safe removal)
            for layer_info in self.layers.values():
                layer_info["elements"].remove(identifier)

            # Remove from all groups (sets)
            for element_ids in self.groups.values():
                element_ids.discard(identifier)  # safe, no error

    def clear_layer(self, layer):
        if layer in self.layers:
            identifiers = self.layers[layer]["elements"].copy()
            self.remove_elements(identifiers)
            del self.layers[layer]

    def clear_group(self, group):
        if group in self.groups:
            identifiers = list(self.groups[group])  # copy
            self.remove_elements(identifiers)
            del self.groups[group]

    def get_elements(
        self, *, identifiers=None, groups=None, layers=None, require_all=False
    ):
        """
        Flexible query system.
        Returns element *instances* matching ANY or ALL filters.

        identifiers: str or list[str]
        groups: str or list[str]
        layers: str or list[str]
        require_all: if True, element must match ALL conditions instead of ANY
        """

        id_filter = self._norm_set(identifiers)
        group_filter = self._norm_set(groups)
        layer_filter = self._norm_set(layers)

        if not id_filter and not group_filter and not layer_filter:
            return list(self.elements.values())

        group_hits = set()
        for g in group_filter:
            group_hits |= self.groups.get(g, set())

        layer_hits = set()
        for lf in layer_filter:
            layer_hits |= set(self.layers.get(lf, {}).get("elements", []))

        results = []
        for ident, elem in self.elements.items():
            match_ident = (not id_filter) or (ident in id_filter)
            match_group = (not group_filter) or (ident in group_hits)
            match_layer = (not layer_filter) or (ident in layer_hits)

            matches = (match_ident, match_group, match_layer)

            if require_all and all(matches):
                results.append(elem)
            elif not require_all and any(matches):
                results.append(elem)

        return results

    def render(self, global_op=None):
        for layer_name, layer_info in self.layers.items():
            self._render_layer(layer_name, layer_info, global_op)
        return self._image

    def _render_layer(self, layer_name, layer_info, global_op=None):
        # TODO: apply layer settings

        for identifier in layer_info["elements"]:
            e = self.elements.get(identifier)
            if e is None:
                logger.error(
                    f"Element '{identifier}' listed in layer {layer_name} not found in registry."
                )
                continue
            
            if e.is_ready():
                if global_op is not None:
                    global_op(e)
                    
                logger.debug("CANVAS: Drawing element '%s' in layer '%s'", identifier, layer_name)
                e.draw(self._draw, self._image)
            else:
                logger.error(
                    f"Element '{identifier}' in layer {layer_name} is not ready and will be skipped."
                )

    # helpers
    def _norm_set(self, value):
        if value is None:
            return set()
        if isinstance(value, str):
            return {value}
        return set(value)

    def populate_layer_by_info(self, name: str, layer_info: dict):
        """
        layer_dict structure:
        {
            "opacity": 1.0,
            "elements": {
                "full_bg": {...},
                "title1": {...},
                "subtitle1": {...}
            }
        }
        """
        logger.debug(f"CANVAS: Populating layer '{name}' with elements")

        settings = {}
        elements = layer_info.get("elements", {})

        # Extract settings (e.g. opacity)
        for k, v in layer_info.items():
            if k != "elements":
                settings[k] = v

        # Create layer record
        if name not in self.layers:
            self.layers[name] = {"settings": settings, "elements": []}

        # Build all elements under this layer
        for identifier, element_info in elements.items():
            logger.debug("CANVAS: Iterating element: %s %r", identifier, element_info)

            groups = element_info.get("groups", [])
            element = self._build_element(element_info)
            self.add_element(identifier, element, groups=groups, layer=name)

    def _build_element(self, element_info: dict):
        """
        Convert YAML dict → Element instance.
        Replace this with your real Element classes.
        """
        element_type = element_info.get("type")
        
        element = get_factory().create_element(
            element_type,
            position=element_info.get("position"),
            values=element_info.get("values", {}),
        )
        
        # apply operations
        operations = element_info.get("operations", {})
        factory = get_operation_factory()
        
        for op_name, op_params in operations.items():
            op_entry = factory.get_operation(op_name)
            if op_entry is None:
                logger.error(f"Operation '{op_name}' not found in factory.")
                continue
            
            if element_type not in op_entry["supported_types"]:
                logger.error(f"Operation '{op_name}' not supported for element type '{element_type}'.")
                continue
            
            operation = op_entry["func"]
            
            element.apply_operation(lambda img, op=operation, params=op_params: op(img, **params))

        
        return element
        
    @staticmethod
    def from_dict(data: dict) -> "Canvas":
        width = data.get("width", 1080)
        height = data.get("height", 1350)
        background = data.get("background", "#fff")

        canvas = Canvas(width=width, height=height, background=background)

        return canvas
