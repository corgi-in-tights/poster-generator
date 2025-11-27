import json
from pathlib import Path

import yaml

from .loader import LayerBasedLoader


class YamlLoader(LayerBasedLoader):
    """
    Canvas loader for YAML configuration files.
    """

    def read_source(self, path: str) -> dict:
        with Path(path).open() as f:
            return yaml.safe_load(f)


class JsonLoader(LayerBasedLoader):
    """
    Canvas loader for JSON configuration files.
    """

    def read_source(self, path: str) -> dict:
        with Path(path).open() as f:
            return json.load(f)

