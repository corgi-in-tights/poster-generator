SHORT_HEX_LENGTH = 3
HEX_RGB_LENGTH = 6
HEX_RGBA_LENGTH = 8
RGB_TUPLE_LENGTH = 3
RGBA_TUPLE_LENGTH = 4
DEFAULT_ALPHA = 255


def normalize_color(color_input: str | tuple | dict | None) -> tuple | None:
    """
    Normalize a color input to an RGBA tuple.

    Args:
        color_input (str | tuple): Color input as a hex string or an RGBA tuple.

    Returns:
        tuple: Normalized RGBA tuple.
    """
    if color_input is None:
        return None

    if isinstance(color_input, str):
        color_input = color_input.lstrip("#")
        lv = len(color_input)

        if lv == SHORT_HEX_LENGTH:
            r, g, b = tuple(int(color_input[i] * 2, 16) for i in range(3))
            return (r, g, b, DEFAULT_ALPHA)

        if lv == HEX_RGB_LENGTH:
            r, g, b = tuple(int(color_input[i:i + 2], 16) for i in (0, 2, 4))
            return (r, g, b, DEFAULT_ALPHA)

        if lv == HEX_RGBA_LENGTH:
            r, g, b, a = tuple(int(color_input[i:i + 2], 16) for i in (0, 2, 4, 6))
            return (r, g, b, a)

        msg = "Hex color must be in format RRGGBB or RRGGBBAA"
        raise ValueError(msg)

    if isinstance(color_input, tuple) and (RGB_TUPLE_LENGTH <= len(color_input) <= RGBA_TUPLE_LENGTH):
        return color_input + (() if len(color_input) == RGBA_TUPLE_LENGTH else (DEFAULT_ALPHA,))

    if isinstance(color_input, dict):
        r = color_input.get("r") or color_input.get("red")
        g = color_input.get("g") or color_input.get("green")
        b = color_input.get("b") or color_input.get("blue")
        a = color_input.get("a") or color_input.get("alpha", DEFAULT_ALPHA)
        if r is not None and g is not None and b is not None:
            return (r, g, b, a)

    msg = "Color input must be a hex string or an RGB/RGBA tuple"
    raise ValueError(msg)
