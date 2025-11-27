def get_alignment_position(  # noqa: PLR0913
    element_size,
    parent_size,
    x_align: float | None,
    y_align: float | None,
    parent_position=(0, 0),
    original_position=(0, 0),

):
    width, height = element_size
    parent_x, parent_y = parent_position
    parent_width, parent_height = parent_size
    default_x, default_y = original_position

    new_x = (
        default_x if x_align is None
        else x_align * (parent_width - width) + parent_x
    )
    new_y = (
        default_y if y_align is None
        else y_align * (parent_height - height) + parent_y
    )

    return (new_x, new_y)
