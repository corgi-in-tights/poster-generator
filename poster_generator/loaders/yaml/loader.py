"""YAML-based canvas configuration loader."""

import logging
from pathlib import Path

import yaml

from poster_generator.canvas import Canvas
from poster_generator.loaders.base import BaseCanvasLoader
from poster_generator.utils import get_alignment_position

from .resolver import YamlResolver

logger = logging.getLogger(__name__)


class YamlLoader(BaseCanvasLoader):
    """
    Canvas loader for YAML configuration files.
    """

    SCHEMA_VERSION = "1.0"

    def read_source(self, path: str) -> dict:
        with Path(path).open() as f:
            return yaml.safe_load(f)

    def deserialize(self, data: dict, variables: dict) -> Canvas:
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
        schema = data.get("schema", YamlLoader.SCHEMA_VERSION)
        if schema != YamlLoader.SCHEMA_VERSION:
            msg = f"Unsupported schema version: {schema}. Current version is {YamlLoader.SCHEMA_VERSION}."
            raise ValueError(msg)

        logger.debug("Deserializing YAML canvas configuration.")

        deserialized_info = {}

        self.yaml_resolver = YamlResolver(variables)
        self.resolve_variable = self.yaml_resolver.resolve_variable  # shortcut

        deserialized_info["settings"] = self._deserialize_settings(data)
        logger.debug("Canvas settings: %s", deserialized_info["settings"])

        deserialized_info["anchors"] = self._deserialize_anchors(data)
        logger.debug("Canvas anchors: %s", deserialized_info["anchors"])

        deserialized_info["layers"], deserialized_info["elements"] = self._deserialize_layers_elements(data)

        logger.debug(
            "Deserialized %i layers and %i elements.",
            len(deserialized_info["layers"]),
            len(deserialized_info["elements"]),
        )

        self.yaml_resolver = None
        self.resolve_variable = None

        return deserialized_info

    def _deserialize_settings(self, data: dict):
        settings_data = data.get("settings", {})
        width = int(self.resolve_variable(settings_data.get("width", 1080)))
        height = int(self.resolve_variable(settings_data.get("height", 1350)))
        background = self.resolve_variable(settings_data.get("background", "#fff"), key="background")
        return {"width": width, "height": height, "background": background}

    def _deserialize_anchors(self, data: dict):
        anchors = {}
        for anchor_id, anchor_data in data.get("anchors", {}).items():
            anchors[anchor_id] = self.yaml_resolver.resolve_point(anchor_data)
        return anchors

    def _deserialize_layers_elements(self, data: dict):
        layer_info = {}
        element_info = {}

        for layer_name, layer_data in data.get("layers", {}).items():
            logger.debug("Deserializing layer: %s", layer_name)
            layer_info[layer_name] = self._parse_layer_settings(layer_data.get("settings", {}))

            elements_data = layer_data.get("elements")
            if elements_data is None:
                msg = f"Layer '{layer_name}' must have an 'elements' section."
                raise ValueError(msg)

            for element_id, element_data in elements_data.items():
                logger.debug("Deserializing element: %s in layer: %s", element_id, layer_name)
                element_info[element_id] = self._parse_element(element_id, element_data, layer_name)

            logger.debug("Deserialized %i elements for layer %s", len(elements_data), layer_name)

        return layer_info, element_info

    def _parse_layer_settings(self, layer_settings: dict):
        """
        Returns:
            {
                "opacity": float (0.0 to 1.0),
            }
        """
        opacity = max(
            0.0,
            min(1.0, float(self.resolve_variable(layer_settings.get("opacity", 1)))),
        )
        return {
            "opacity": opacity,
        }

    def _parse_element(self, element_id: str, element_data: dict, layer_name: str):
        """
        Returns:
            {
                "type": str,
                "groups": list[str],
                "layer": str,
                "values": dict,
                "operations": dict,
                "position": (x, y) | "rel_position": {
                                        "source": str,
                                        "value": ...,
                                        "offset": (x, y),
                                        "parent": str | None}
                                    }
        """
        logger.debug("Parsing element %s of type %s", element_id, element_data.get("type"))
        element_info = {}

        element_type = element_data.get("type")
        if element_type is None:
            msg = f"Element '{element_id}' must have a 'type' specified."
            raise ValueError(msg)

        element_info["type"] = element_type
        element_info["layer"] = layer_name
        element_info["groups"] = element_data.get("groups", [])

        values = {}
        for k, v in element_data.get("values", {}).items():
            values[k] = self.yaml_resolver.deep_resolve_variables(v, key=k)
        element_info["values"] = values

        operations = {}
        for ko, vo in element_data.get("operations", {}).items():
            operations[ko] = self.yaml_resolver.deep_resolve_variables(vo)
        element_info["operations"] = operations

        # Support late relative positions
        if "position" in element_data:
            element_info["position"] = self.yaml_resolver.resolve_point(element_data["position"])
        elif "rel_position" in element_data:
            rel_position_data = element_data["rel_position"]
            element_info["rel_position"] = self._parse_element_relative_position(element_id, rel_position_data)
        else:
            element_info["position"] = (0, 0)

        logger.debug("Element %s info: %s", element_id, element_info)
        return element_info

    def _parse_element_relative_position(self, element_id: str, rel_position_data: dict):
        source = self.resolve_variable(rel_position_data.get("source"))
        if source is None:
            msg = f"For element {element_id}, 'source' must be specified for relative positioning."
            raise ValueError(msg)

        source_value = self.yaml_resolver.deep_resolve_variables(rel_position_data.get("value"))
        if source_value is None:
            msg = f"For element {element_id}, 'value' must be specified for relative positioning."
            raise ValueError(msg)

        if "offset" in rel_position_data:
            offset = self.yaml_resolver.resolve_point(rel_position_data.get("offset"), default_x=0, default_y=0)
        else:
            offset = (0, 0)

        # For specific parent element alignment
        parent = self.resolve_variable(rel_position_data.get("parent"))

        return {
            "source": source,
            "value": source_value,
            "offset": offset,
            "parent": parent,
        }

    def _calculate_element_position(
        self,
        element_id: str,
        element,
        rel_position_info: dict,
        anchors: dict,
        canvas: Canvas,
    ):
        source = rel_position_info.get("source")
        if source is None:
            msg = f"For element '{element_id}', 'source' must be specified in relative position info."
            raise ValueError(msg)

        value = rel_position_info.get("value")
        if value is None:
            msg = f"For element '{element_id}', 'value' must be specified in relative position info."
            raise ValueError(msg)

        offset = rel_position_info.get("offset", (0, 0))

        if source == "anchor":
            position = self._resolve_anchor_position(element_id, value, anchors)
        elif source == "element":
            position = self._resolve_element_reference_position(element_id, value, canvas)
        elif source == "alignment":
            position = self._resolve_alignment_position(element, value, rel_position_info, canvas)
        else:
            msg = f"For element {element_id}, unsupported relative position source '{source}'."
            raise ValueError(msg)

        logger.debug("Calculated position for element %s: %s", element_id, position)
        return (position[0] + offset[0], position[1] + offset[1])

    def _resolve_anchor_position(self, element_id: str, anchor_name: str, anchors: dict):
        """Resolve position from an anchor."""
        if not isinstance(anchor_name, str):
            msg = f"For element '{element_id}', anchor name must be a string."
            raise TypeError(msg)

        anchor_position = anchors.get(anchor_name)
        if anchor_position is None:
            msg = f"For element '{element_id}', anchor '{anchor_name}' was not found."
            raise ValueError(msg)

        return anchor_position

    def _resolve_element_reference_position(self, element_id: str, ref_element_id: str, canvas: Canvas):
        """Resolve position from another element."""
        if not isinstance(ref_element_id, str):
            msg = f"For element '{element_id}', reference element ID must be a string."
            raise TypeError(msg)

        ref_element = canvas.elements.get(ref_element_id)
        if ref_element is None:
            msg = f"Element '{ref_element_id}' not found for relative positioning of element '{element_id}'."
            raise ValueError(msg)

        return ref_element.position

    def _resolve_alignment_position(self, element, value, rel_position_info: dict, canvas: Canvas):
        """Resolve position from alignment configuration."""
        # Use a private resolver
        yaml_resolver = YamlResolver({})  # No variables needed here
        logger.debug("Resolving alignment position with value: %s", value)

        x_align, y_align = yaml_resolver.resolve_point(value, default_x=None, default_y=None)

        parent_element_id = rel_position_info.get("parent")
        parent_element = canvas.get_first_element(identifier=parent_element_id) if parent_element_id else None

        return get_alignment_position(
            element_size=element.get_size(),
            parent_size=parent_element.get_size() if parent_element else canvas.get_size(),
            x_align=x_align,
            y_align=y_align,
            parent_position=parent_element.position if parent_element else (0, 0),
            original_position=element.position,
        )

    def post_build_element(self, element_id, element, canvas, element_info, deserialized_info):
        if "rel_position" in element_info:
            logger.debug(
                "Post-processing element %s for relative position resolution with info: %s",
                element_id,
                element_info["rel_position"],
            )
            pos = self._calculate_element_position(
                element_id,
                element,
                element_info["rel_position"],
                deserialized_info.get("anchors", {}),
                canvas,
            )
            element.update_position(pos)
            del element_info["rel_position"]
