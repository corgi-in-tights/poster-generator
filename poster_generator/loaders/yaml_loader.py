"""YAML-based canvas configuration loader."""

import logging
import yaml

from .base import BaseCanvasLoader
from ..canvas import Canvas

logger = logging.getLogger(__name__)


class YamlLoader(BaseCanvasLoader):
    """
    Canvas loader for YAML configuration files.
    """

    SCHEMA_VERSION = "1.0"

    def read_source(self, path: str) -> dict:
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def deserialize(self, raw_data: dict, variables: dict) -> Canvas:
        """
        Deserialize YAML data into a normalized canvas configuration.

        Args:
            raw_data: Raw YAML data as a dictionary.
            variables: Dictionary for variable substitution.

        Returns:
            dict: Normalized configuration with settings, anchors, and layers.

        Raises:
            ValueError: If the schema version is unsupported.
        """
        schema = raw_data.get("schema", YamlLoader.SCHEMA_VERSION)
        if schema != YamlLoader.SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported schema version: {schema}. "
                f"Current version is {YamlLoader.SCHEMA_VERSION}."
            )

        # To avoid passing it around everywhere
        self._variables = variables

        _settings = self._deserialize_settings(raw_data)

        self._canvas = canvas = Canvas.from_dict(_settings)

        anchors = self._deserialize_anchors(raw_data)

        layers_raw = raw_data.get("layers", {})
        while len(layers_raw) > 0:
            layer_name, raw_layer_data = next(iter(layers_raw.items()))
            layer_data = self._parse_layer(raw_layer_data)

            canvas.add_layer(layer_name, layer_data["settings"])

            for element_id, element_data in layer_data["elements"].items():
                element_info = self._parse_element(
                    element_id, element_data, anchors, canvas.elements
                )

                groups = element_info.get("groups", [])
                element = self.build_element(element_id, element_info)

                # Resolve relative positions
                if "rel_position" in element_info:
                    pos = self._resolve_element_position(
                        element_id,
                        element,
                        element_info["rel_position"],
                        anchors,
                        canvas,
                    )
                    element.update_position(pos)

                canvas.add_element(
                    element_id,
                    element,
                    groups=groups,
                    layer=layer_name,
                )

        self._variables = None
        self._canvas = None

        return canvas

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
        background = self.ensure_value(settings_data.get("background", "#fff"))
        return {"width": width, "height": height, "background": background}

    def _parse_point(self, point_data):
        if isinstance(point_data, dict):
            x = int(self.ensure_value(point_data.get("x", 0)))
            y = int(self.ensure_value(point_data.get("y", 0)))
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

    def _parse_layer(self, layer_data: dict):
        raw_settings = layer_data.get("settings", {})

        opacity = max(
            0.0, min(1.0, float(self.ensure_value(raw_settings.get("opacity", 1))))
        )

        return {
            "settings": {"opacity": opacity},
            "elements": layer_data.get("elements", {}),
        }

    def _parse_element(self, element_id, element_data):
        # type is image, text, shape, etc.
        element_type = element_data["type"]

        groups = element_data.get("groups", [])

        values = {
            k: self.ensure_value(v) for k, v in element_data.get("values", {}).items()
        }

        operations = {
            k: {ok: self.ensure_value(ov) for ok, ov in v.items()}
            for k, v in element_data.get("operations", {}).items()
        }

        element_info = {
            "type": element_type,
            "groups": groups,
            "values": values,
            "operations": operations,
        }

        # Calculate it later to support size-based alignments
        if "position" in element_data:
            element_info["position"] = self._parse_point(element_data.get("position"))
        elif "rel_position" in element_data:
            r = element_data.get("rel_position")
            rd = {}

            rd["source"] = self.ensure_value(r.get("source"))
            rd["value"] = self.ensure_value(r.get("value"))
            rd["offset"] = self._parse_point(r.get("offset", {"x": 0, "y": 0}))
            rd["parent"] = self.ensure_value(r.get("parent", None))

            element_info["rel_position"] = rd

        return element_info

    def _resolve_element_position(
        self,
        element_id: str,
        element,
        rel_position_info: dict,
        anchors: dict,
        canvas: Canvas,
    ):
        source = rel_position_info["source"]
        value = rel_position_info["value"]
        offset = rel_position_info.get("offset", (0, 0))

        if source == "anchor":
            if value not in anchors:
                raise ValueError(
                    f"For element {element_id}, anchor '{value}' was not found'."
                )
            anchor_pos = anchors.get(value)
            position = (anchor_pos[0], anchor_pos[1])

        elif source == "element":
            if value not in canvas.elements:
                raise ValueError(
                    f"Element '{value}' not found for relative positioning of element '{element_id}'."
                )

            ref_element_info = canvas.get_first_element(identifier=value)
            position = (
                ref_element_info.position[0],
                ref_element_info.position[1],
            )

        elif source == "alignment":
            position = element.get_alignment_position(
                canvas,
                parent_element_id=rel_position_info.get("parent", None),
                x_align=value.get("x_align", "auto"),
                y_align=value.get("y_align", "auto"),
            )

        else:
            msg = f"For element {element_id}, unsupported relative position source '{source}'."
            raise ValueError(msg)

        position = (
            position[0] + offset[0],
            position[1] + offset[1],
        )

        return position
