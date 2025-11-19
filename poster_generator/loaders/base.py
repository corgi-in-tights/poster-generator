from abc import ABC, abstractmethod

from poster_generator import Canvas
from ..settings import get_logger

logger = get_logger()

class CanvasLoader(ABC):
    """
    Abstract format-agnostic loader.
    Subclasses only need to implement:
       - _read_source(): turns path → raw_data (dict)
       - deserialize_canvas(): turns raw_data → normalized canvas
    """

    def build_canvas(self, source, variables=None):
        """
        Public API. Accepts:
            - source: file path OR already-loaded dict
            - variables: optional dict for placeholder substitution
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
        If the user passes a file path, read it.
        If the user passes a dict, use it directly.
        """
        if isinstance(source, str):
            return self._read_source(source)
        elif isinstance(source, dict):
            return source
        else:
            raise TypeError(f"Invalid source type: {type(source)}")

    @abstractmethod
    def _read_source(self, path: str) -> dict:
        """Read raw data from file (YAML, JSON, TOML, DB, etc.)."""
        pass

    @abstractmethod
    def deserialize(self, raw_data: dict, variables: dict) -> dict:
        """Format-agnostic normalization step."""
        pass

    def preprocess(self, raw_data: dict, variables: dict) -> dict:
        """Override to validate or transform raw data."""
        return raw_data

    def postprocess(self, canvas: dict, variables: dict) -> dict:
        """Override to transform or annotate the final canvas."""
        return canvas
