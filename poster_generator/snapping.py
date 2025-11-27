from typing import NamedTuple


class ParentBounds(NamedTuple):
    width: int
    height: int
    x: int = 0
    y: int = 0

class ElementSize(NamedTuple):
    width: int
    height: int
    default_x: int = 0
    default_y: int = 0

class AlignmentOptions(NamedTuple):
    x_align: float | None = 0.0
    y_align: float | None = 0.0


def get_alignment_position(
    parent: ParentBounds,
    element: ElementSize,
    options: AlignmentOptions | None = None,
):
    """
    Get the position (x, y) to align an element within the canvas based on specified horizontal and vertical alignment.

    Args:
        parent (ParentBounds): The bounds of the parent container (width, height, x, y).
        elem (ElementSize): The size of the element to be aligned (width, height).
        options (AlignmentOptions, optional): Alignment options including x_align, y_align, auto_x, auto_y.

    Returns:
        A tuple (x, y) representing the calculated position for the element.
    """
    if options is None:
        options = AlignmentOptions()

    new_x = (
        options.default_x if options.x_align is None
        else options.x_align * (parent.width - element.width) + parent.x
    )
    new_y = (
        options.default_y if options.y_align is None
        else options.y_align * (parent.height - element.height) + parent.y
    )

    return (new_x, new_y)
