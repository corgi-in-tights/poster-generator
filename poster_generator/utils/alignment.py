import logging

logger = logging.getLogger(__name__)


def get_alignment_position(  # noqa: PLR0913
    element_size,
    parent_size,
    x_align: float | None,
    y_align: float | None,
    parent_position=(0, 0),
    original_position=(0, 0),
):
    """
    Calculate the new position of an element based on alignment parameters.

    Args:
        element_size (tuple): Size of the element as (width, height).
        parent_size (tuple): Size of the parent container as (width, height).
        x_align (float or None): Horizontal alignment factor (0.0 to 1.0) or None (default to original x position).
        y_align (float or None): Vertical alignment factor (0.0 to 1.0) or None (default to original y position).
        parent_position (tuple): Position of the parent container as (x, y). Defaults to (0, 0).
        original_position (tuple): Original position of the element as (x, y). Defaults to (0, 0).

    Returns:
        tuple: New position of the element as (x, y).
    """
    logger.debug(
        "Calculating alignment position with element_size=%s, parent_size=%s, x_align=%s, y_align=%s, "
        "parent_position=%s, original_position=%s",
        element_size,
        parent_size,
        x_align,
        y_align,
        parent_position,
        original_position,
    )

    width, height = element_size
    parent_x, parent_y = parent_position
    parent_width, parent_height = parent_size
    default_x, default_y = original_position

    new_x = default_x if x_align is None else x_align * (parent_width - width) + parent_x
    new_y = default_y if y_align is None else y_align * (parent_height - height) + parent_y

    logger.debug("Calculated new position: (%s, %s)", new_x, new_y)

    return (new_x, new_y)
