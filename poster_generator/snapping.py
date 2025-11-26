def get_alignment_position(canvas_width, canvas_height, elem_width, elem_height, x_align="auto", y_align="auto", auto_x=0, auto_y=0):
    """
    Get the position (x, y) to align an element within the canvas based on specified horizontal and vertical alignment.
    
    Args:
        canvas_width (int): The width of the canvas.
        canvas_height (int): The height of the canvas.
        elem_width (int): The width of the element to be aligned.
        elem_height (int): The height of the element to be aligned.
        x_align (str, optional): Horizontal alignment option - "left", "center", or "right". Defaults to "center".
        y_align (str, optional): Vertical alignment option - "top", "center", or "bottom". Defaults to "center".
        auto_x (int, optional): The original x position if x_align is "auto". Defaults to 0.
        auto_y (int, optional): The original y position if y_align is "auto". Defaults to 0.
        
    Returns:
        A tuple (x, y) representing the calculated position for the element.
    
    Raises:   
        ValueError: If invalid alignment options are provided for x_align or y_align.
    """
    # Calculate new x position
    if x_align == "auto": 
        new_x = auto_x
    elif x_align == "left":
        new_x = 0
    elif x_align == "center":
        new_x = (canvas_width - elem_width) // 2
    elif x_align == "right":
        new_x = canvas_width - elem_width
    else:
        raise ValueError(f"Invalid x_align value: {x_align}")

    # Calculate new y position
    if y_align == "auto":
        new_y = auto_y
    elif y_align == "top":
        new_y = 0
    elif y_align == "center":
        new_y = (canvas_height - elem_height) // 2
    elif y_align == "bottom":
        new_y = canvas_height - elem_height
    else:
        raise ValueError(f"Invalid y_align value: {y_align}")

    return (new_x, new_y)