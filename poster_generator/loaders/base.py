"""Base abstract loader for creating canvases from various data sources."""

import logging
from abc import ABC, abstractmethod

from poster_generator.canvas import Canvas
from poster_generator.factories.element import get_element_factory
from poster_generator.factories.operation import get_operation_factory

logger = logging.getLogger(__name__)


class BaseCanvasLoader(ABC):
    """
    Abstract base class for loading canvas configurations from various formats.

    Subclasses must implement:
        - read_source(): Converts a file path to raw data (dict)
        - deserialize(): Converts raw data to normalized canvas configuration

    Subclasses may optionally override:
        - preprocess(): Transform raw data before deserialization
        - pre_build_element(): Modify element info before building
        - post_build_element(): Process element after building, before adding to canvas
        - post_build_canvas(): Final processing after canvas is fully built
    """

    def build_canvas(self, source, variables=None):
        """
        Build a Canvas instance from a file path or dictionary.

        This is the main public API for loading canvases. It handles reading the source,
        deserializing the data, and constructing the Canvas with all elements.

        Args:
            source: Either a file path (str) or an already-loaded dictionary.
            variables: Optional dict for variable substitution in the configuration.

        Returns:
            Canvas: Fully configured Canvas instance with all elements loaded.
        """
        data = self._prepare_source(source)
        deserialized_info = self.deserialize(data, variables or {})

        logger.debug("Building Canvas from deserialized data with keys: %s", list(deserialized_info.keys()))

        settings = deserialized_info.get("settings", {})
        canvas = Canvas.from_dict(settings)

        layers = deserialized_info.get("layers", {})
        for layer_name, layer_settings in layers.items():
            canvas.add_layer(layer_name, layer_settings)

        elements = deserialized_info.get("elements", {})
        for element_id, element_info in elements.items():
            logger.debug("Building element '%s' of type '%s'.", element_id, element_info.get("type"))

            element_info = self.pre_build_element(element_id, element_info, canvas, deserialized_info)  # noqa: PLW2901
            if element_info is None:
                logger.debug("Element %s skipped by pre_build_element hook.", element_id)
                continue

            layer = element_info.get("layer")
            groups = element_info.get("groups", [])

            element = self.build_element(element_id, element_info)
            self.post_build_element(element_id, element, canvas, element_info, deserialized_info)
            logger.debug("Adding element '%s' to canvas on layer '%s'.", element_id, layer)

            canvas.add_element(element_id, element, layer=layer, groups=groups)

        self.post_build_canvas(canvas, deserialized_info)

        logger.info("Canvas built with %d layers and %d elements.", len(canvas.layers), len(canvas.elements))

        return canvas

    def _prepare_source(self, source):
        """
        Prepare the source data for processing.

        Args:
            source: Either a file path (str) or a dictionary.

        Returns:
            dict: Raw data dictionary.

        Raises:
            TypeError: If source is neither a string nor a dictionary.
        """
        if isinstance(source, str):
            return self.read_source(source)
        if isinstance(source, dict):
            return source

        msg = f"Invalid source type: {type(source)}"
        raise TypeError(msg)

    @abstractmethod
    def read_source(self, path: str) -> dict:
        """
        Read and parse a file into a raw data dictionary.

        Args:
            path: Path to the file to read.

        Returns:
            dict: Raw parsed data from the file.
        """

    @abstractmethod
    def deserialize(self, raw_data: dict, variables: dict) -> dict:
        """
        Convert raw data into a normalized canvas configuration.

        Args:
            raw_data: The raw parsed data from the source.
            variables: Dictionary for variable substitution.

        Returns:
            dict: Normalized canvas configuration with keys:
            - settings: dict of canvas settings
            - layers: dict of layer definitions
            - elements: dict of element definitions
        """

    def pre_build_element(
        self,
        element_id: str,
        element_info: dict,
        canvas: Canvas,
        deserialized_info: dict,
    ) -> dict | None:
        """
        Hook for pre-processing element info before building the element.

        Args:
            element_id: The identifier of the element.
            element_info: The raw element data from the deserialized configuration.
            canvas: The Canvas instance being built.
            deserialized_info: The full deserialized canvas data.

        Returns:
            dict: Modified element_info to use for building, or None to skip this element.
        """
        return element_info

    def build_element(self, element_id: str, element_info: dict):
        """
        Convert YAML dict into an Element instance.

        Format:
            {
                "type": str,
                "values": dict, (optional)
                "operations": dict, (optional)
                "position": (x, y), (optional)
        """
        element_type = element_info.get("type")

        element = get_element_factory().create_element(
            element_type,
            position=element_info.get("position"),
            values=element_info.get("values", {}),
        )

        # Apply operations
        operations = element_info.get("operations", {})
        factory = get_operation_factory()

        for op_name, op_kwargs in operations.items():
            op_entry = factory.get_operation(op_name)
            if op_entry is None:
                logger.warning("For element %s, operation '%s' not found in factory. Skipping.", element_id, op_name)
                continue

            if element_type not in op_entry["supported_types"]:
                logger.warning(
                    "For element %s, operation '%s' not supported for element type '%s'. Skipping.",
                    element_id,
                    op_name,
                    element_type,
                )
                continue

            logger.debug("Applying operation '%s' to element '%s'.", op_name, element_id)
            element.apply_operation(op_entry["func"], kwargs=op_kwargs)

        return element

    def post_build_element(  # noqa: B027
        self,
        element_id: str,
        element,
        canvas: Canvas,
        element_info: dict,
        deserialized_info: dict,
    ):
        """
        Hook for post-processing an element before it is added to the canvas.

        Args:
            element_id: The identifier of the element.
            element: The element instance that was built.
            canvas: The Canvas instance the element will be added to.
            element_info: The raw element data from the deserialized configuration.
            deserialized_info: The full deserialized canvas data.
        """

    def post_build_canvas(  # noqa: B027
        self,
        canvas: Canvas,
        deserialized_info: dict,
    ):
        """
        Hook for final processing after the canvas is fully built.

        Useful for validation, linking elements together, or applying global transformations.

        Args:
            canvas: The fully built Canvas instance.
            deserialized_info: The full deserialized canvas data.
        """
