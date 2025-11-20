"""Image transformation operations for color manipulation."""

import colorsys
from PIL import Image


def ensure_rgba(image: Image) -> Image:
    """
    Ensure an image is in RGBA mode.
    
    Args:
        image: PIL Image in any mode.
    
    Returns:
        PIL Image in RGBA mode.
    """
    if image.mode != "RGBA":
        return image.convert("RGBA")
    return image


def apply_hue_shift(image_obj, degrees: float):
    """
    Shift the hue of an image by a specified number of degrees.
    
    Args:
        image_obj: Dict containing a PIL Image under the key "image".
        degrees: Number of degrees to shift the hue (0-360).
    
    Returns:
        PIL Image with shifted hue in RGBA mode.
    """
    image = image_obj["image"]
    hsv = ensure_rgba(image).convert("HSV")
    
    h, s, v = hsv.split()
    hue_shift_pixels = h.point(lambda p: (p + int(degrees * 255 / 360)) % 256)
    
    hsv = Image.merge("HSV", (hue_shift_pixels, s, v))
    
    image_obj["image"] = hsv.convert("RGBA")
    
    
def set_hue_from_hex(image_obj, hex_color: str):
    """
    Replace the hue of all pixels with the hue from a hex color.
    
    Preserves the saturation and value of each pixel while replacing only the hue
    component with the hue from the specified hex color.
    
    Args:
        image_obj: Dict containing a PIL Image under the key "image".
        hex_color: Hex color string (e.g., "#FF5733" or "FF5733").
    
    Returns:
        PIL Image with replaced hue in RGBA mode.
    """
    image = image_obj["image"]
    
    pixels = ensure_rgba(image).load()
    width, height = image.size
    
    hex_color = hex_color.lstrip("#")
    r_hex = int(hex_color[0:2], 16)
    g_hex = int(hex_color[2:4], 16)
    b_hex = int(hex_color[4:6], 16)

    target_h, _, _ = colorsys.rgb_to_hsv(
        r_hex / 255.0, g_hex / 255.0, b_hex / 255.0
    )

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # convert pixel to HSV
            h, s, v = colorsys.rgb_to_hsv(
                r / 255.0, g / 255.0, b / 255.0
            )

            # replace hue
            h = target_h

            # convert back to RGB
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)

            pixels[x, y] = (
                int(r2 * 255),
                int(g2 * 255),
                int(b2 * 255),
                a,
            )
            
    image_obj["image"] = image