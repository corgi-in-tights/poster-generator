def get_alignment_position(
    parent_width,
    parent_height,
    elem_width,
    elem_height,
    parent_x=0,
    parent_y=0,
    x_align=0.0,
    y_align=0.0,
    auto_x=0,
    auto_y=0,
):
    """
    Get the position (x, y) to align an element within the canvas based on specified horizontal and vertical alignment.

    Args:
        parent_width (int): The width of the canvas.
        parent_height (int): The height of the canvas.
        elem_width (int): The width of the element to be aligned.
        elem_height (int): The height of the element to be aligned.
        parent_x (int, optional): The x offset of the parent. Defaults to 0.
        parent_y (int, optional): The y offset of the parent. Defaults to 0.
        x_align (float, optional): Horizontal alignment (0.0 = left, 0.5 = center, 1.0 = right). Defaults to 0.0.
        y_align (float, optional): Vertical alignment (0.0 = top, 0.5 = center, 1.0 = bottom). Defaults to 0.0.
        auto_x (int, optional): The x position to use if x_align is None. Defaults to 0.
        auto_y (int, optional): The y position to use if y_align is None. Defaults to 0.

    Returns:
        A tuple (x, y) representing the calculated position for the element.
    """
    if x_align is None:
        new_x = auto_x
    else:
        new_x = x_align * (parent_width - elem_width) + parent_x
    
    if y_align is None:
        new_y = auto_y
    else:
        new_y = y_align * (parent_height - elem_height) + parent_y
    
    return (new_x, new_y)
