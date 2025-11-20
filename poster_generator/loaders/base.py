"""Base abstract loader for creating canvases from various data sources."""

from abc import ABC, abstractmethod

from poster_generator import Canvas
from ..settings import get_logger

logger = get_logger()

class BaseCanvasLoader(ABC):
    """
    Abstract base class for loading canvas configurations from various formats.
    
    Subclasses must implement:
        - _read_source(): Converts a file path to raw data (dict)
        - deserialize(): Converts raw data to normalized canvas configuration
    
    Subclasses may optionally override:
        - preprocess(): Transform raw data before deserialization
        - postprocess(): Transform canvas configuration after deserialization
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
        raw_data = self.preprocess(self._prepare_source(source), variables or {})

        pre_canvas_data = self.deserialize(raw_data, variables or {})

        canvas_data = self.postprocess(pre_canvas_data, variables or {})
        
        logger.debug("CANVAS LOADER: Loaded data %r", canvas_data)

        canvas = Canvas.from_dict(canvas_data["settings"])

        for layer_name, layer_info in canvas_data["layers"].items():
            canvas.populate_layer_by_info(layer_name, layer_info)

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
            return self._read_source(source)
        elif isinstance(source, dict):
            return source
        else:
            raise TypeError(f"Invalid source type: {type(source)}")

    @abstractmethod
    def _read_source(self, path: str) -> dict:
        """
        Read and parse a file into a raw data dictionary.
        
        Args:
            path: Path to the file to read.
        
        Returns:
            dict: Raw parsed data from the file.
        """
        pass

    @abstractmethod
    def deserialize(self, raw_data: dict, variables: dict) -> dict:
        """
        Convert raw data into a normalized canvas configuration.
        
        Args:
            raw_data: The raw parsed data from the source.
            variables: Dictionary for variable substitution.
        
        Returns:
            dict: Normalized canvas configuration with keys: settings, anchors, layers.
        """
        pass

    def preprocess(self, raw_data: dict, variables: dict) -> dict:
        """
        Preprocess raw data before deserialization.
        
        Override this method to add validation or transformation logic.
        
        Args:
            raw_data: The raw parsed data.
            variables: Dictionary for variable substitution.
        
        Returns:
            dict: Preprocessed raw data.
        """
        return raw_data

    def postprocess(self, canvas: dict, variables: dict) -> dict:
        """
        Postprocess the canvas configuration after deserialization.
        
        Override this method to add transformation or annotation logic.
        
        Args:
            canvas: The normalized canvas configuration.
            variables: Dictionary for variable substitution.
        
        Returns:
            dict: Postprocessed canvas configuration.
        """
        return canvas
