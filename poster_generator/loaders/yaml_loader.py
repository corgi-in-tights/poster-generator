import yaml

from .base import CanvasLoader


class YamlLoader(CanvasLoader):
    SCHEMA_VERSION = "1.0"

    def _read_source(self, path: str) -> dict:
        """Load YAML into a dict."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def deserialize_canvas(self, raw_data: dict, variables: dict) -> dict:
        """
        Deserialize a raw YAML dict into a normalized internal canvas model.
        """
        schema = raw_data.get("schema", YamlLoader.SCHEMA_VERSION)
        if schema != YamlLoader.SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported schema version: {schema}. "
                f"Current version is {YamlLoader.SCHEMA_VERSION}."
            )
        
        # to avoid passing it around everywhere    
        self._variables = variables
            
        settings = self._deserialize_settings(raw_data)
        anchors = self._deserialize_anchors(raw_data)
        layers = self._deserialize_layers(raw_data, anchors)

        self._variables = None
        
        return {
            "settings": settings,
            "anchors": anchors,
            "layers": layers,
        }
        
    def ensure_value(self, value):
        if (
            isinstance(value, str)
            and value.startswith("--${")
            and value.endswith("}--")
        ):
            var_name = value[4:-3]
            if var_name in self._variables:
                return self._variables[var_name]
            else:
                raise ValueError(
                    f"Variable '{var_name}' not found in provided variables."
                )
        return value

    def _deserialize_settings(self, data: dict):
        settings_data = data.get("settings", {})
        width = int(self.ensure_value(settings_data.get("width", 1080)))
        height = int(self.ensure_value(settings_data.get("height", 1350)))
        background = self.ensure_value(settings_data.get("background_color", "#fff"))

        return {"width": width, "height": height, "background": background}

    def _parse_point(self, point_data):
        if isinstance(point_data, dict):
            x = int(self.ensure_value(point_data.get("x")))
            y = int(self.ensure_value(point_data.get("y")))

            if x is None or y is None:
                raise ValueError(
                    f"Invalid point data, \
                                    expected x, y integers: {point_data}"
                )

            return (x, y)
        elif isinstance(point_data, list) and len(point_data) == 2:
            return (int(point_data[0]), int(point_data[1]))
        else:
            raise ValueError(f"Invalid point data: {point_data}")

    def _deserialize_anchors(self, data: dict):
        anchors_data = data.get("anchors", {})
        anchors = {}
        for anchor_id, anchor_info in anchors_data.items():
            anchors[anchor_id] = self._parse_point(anchor_info)
        return anchors

    def _deserialize_layers(self, data: dict, anchors: dict):
        layers_data = data.get("layers", {})

        layers = {}
        for layer_name, layer_data in layers_data.items():
            layers[layer_name] = self._parse_layer(layer_data, anchors)

        return layers

    def _parse_layer(self, layer_data: dict, anchors: dict):
        # clamp to [0.0, 1.0]
        opacity = max(
            0.0, min(1.0, float(self.ensure_value(layer_data.get("opacity", 1))))
        )

        elements = layer_data.get("elements", {})
        deserialized_elements = {}

        for element_id, element_info in elements.items():
            deserialized_elements[element_id] = self._parse_element(
                element_id, element_info, anchors, deserialized_elements
            )

        return {
            "opacity": opacity,
            "elements": deserialized_elements,
        }

    def _parse_element(self, element_id, element_data, anchors, deserialized_elements):
        # type is image, text, shape, etc.
        element_type = element_data.get("type")

        groups = element_data.get("groups", [])

        position = self._calculate_element_position(
            element_id, element_data, anchors, deserialized_elements
        )

        values = {
            k: self.ensure_value(v) for k, v in element_data.get("values", {}).items()
        }

        operations = {
            k: {ok: self.ensure_value(ov) for ok, ov in v.items()}
            for k, v in element_data.get("operations", {}).items()
        }

        return {
            "type": element_type,
            "groups": groups,
            "position": position,
            "values": values,
            "operations": operations,
        }

    def _calculate_element_position(
        self, element_id, element_data, anchors, deserialized_elements
    ):
        # position (or rel position if available)
        _position_data = element_data.get("position")
        position = self._parse_point(_position_data) if _position_data else None

        if not position:
            rel_position_info = element_data.get("rel_position")
            if rel_position_info:
                # source can be other elements, anchors, etc.
                # calculated here at loading time to avoid late errors
                source = self.ensure_value(rel_position_info.get("source"))
                source_id = self.ensure_value(rel_position_info.get("id"))

                offset_data = rel_position_info.get("offset", {"x": 0, "y": 0})
                offset = self._parse_point(offset_data)

                if source == "anchor":
                    if source_id not in anchors:
                        raise ValueError(
                            f"Anchor '{source_id}' not found for element '{element_id}'."
                        )
                    anchor_pos = anchors[source_id]
                    position = (anchor_pos[0] + offset[0], anchor_pos[1] + offset[1])
                elif source == "element":
                    # note: this requires that the referenced element has already been processed
                    # but this is a sacrifice im happy to make for simplicity
                    if source_id not in deserialized_elements:
                        raise ValueError(
                            f"Element '{source_id}' not found for relative positioning of element '{element_id}'."
                        )

                    ref_element_info = deserialized_elements[source_id]
                    ref_position = ref_element_info.get("position")
                    if ref_position is None:
                        raise ValueError(
                            f"Referenced element '{source_id}' does not have a defined position for element '{element_id}'."
                        )
                    position = (
                        ref_position[0] + offset[0],
                        ref_position[1] + offset[1],
                    )
                else:
                    raise ValueError(
                        f"Unsupported relative position source '{source}' for element '{element_id}'."
                    )

        return position
