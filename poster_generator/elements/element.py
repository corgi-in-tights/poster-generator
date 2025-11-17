from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image, ImageDraw
    
class CanvasElement(ABC):
    @abstractmethod
    def draw(self, draw: "ImageDraw.Draw", image: "Image.Image", position=None) -> None:
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        pass
