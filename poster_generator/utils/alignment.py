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
