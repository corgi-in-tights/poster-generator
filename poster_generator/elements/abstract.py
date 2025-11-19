from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image, ImageDraw
    
class AbstractDrawableElement(ABC):
    @abstractmethod
    def draw(self, draw: "ImageDraw.Draw", image: "Image.Image", position=None) -> None:
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        pass


    @abstractmethod
    def overlaps_region(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        pass
    
    def overlaps_at(self, x: float, y: float) -> bool:
        eps = 1e-5
        return self.overlaps_region(x, y, x + eps, y + eps)

