# ruff: noqa: PLR2004, INP001
"""Tests for individual element types."""

import pytest
from PIL import Image, ImageDraw

from poster_generator.elements import EllipseElement, ImageElement, RectangleElement, TextElement
from poster_generator.factories.element import ElementFactory

# ==================== TextElement Tests ====================


def test_text_element_initialization():
    """Test basic TextElement initialization."""
    elem = TextElement(position=(100, 50), text="Hello World", font_family="Open Sans", font_size=24, fill="#000000")

    assert elem.position == (100, 50)
    assert elem.text_content == "Hello World"
    assert elem.font_size == 24
    assert elem.fill == (0, 0, 0, 255)


def test_text_element_is_ready_when_all_required_set():
    """Test that TextElement is ready when all required fields are set."""
    elem = TextElement(position=(0, 0), text="Test", font_family="Open Sans", font_size=12)

    assert elem.is_ready() is True


def test_text_element_not_ready_without_text():
    """Test that TextElement is not ready without text."""
    elem = TextElement(position=(0, 0), font_family="Open Sans", font_size=12)

    assert elem.is_ready() is False


def test_text_element_get_size():
    """Test that TextElement.get_size() returns dimensions."""
    elem = TextElement(position=(0, 0), text="Hello", font_family="Open Sans", font_size=24)

    width, height = elem.get_size()

    assert width > 0
    assert height > 0


def test_text_element_wrapping():
    """Test text wrapping with max_width."""
    elem = TextElement(
        position=(0, 0),
        text="This is a very long line of text that should wrap",
        font_family="Open Sans",
        font_size=48,
        max_width=20,
    )

    # With wrapping enabled, height should be greater than single line
    wrapped_height = elem.get_size()[1]

    elem_no_wrap = TextElement(
        position=(0, 0), text="This is a very long line of text that should wrap", font_family="Open Sans",
        font_size=16,
    )
    no_wrap_height = elem_no_wrap.get_size()[1]

    assert wrapped_height > no_wrap_height


def test_text_element_draw():
    """Test that TextElement.draw() renders text to image."""
    elem = TextElement(position=(50, 50), text="Test", font_family="Open Sans", font_size=20, fill="#FF0000")

    img = Image.new("RGBA", (200, 200), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Check that pixels changed (text was drawn)
    # The area around (50, 50) should not be pure white anymore
    pixels_changed = False
    for x in range(50, 100):
        for y in range(50, 70):
            if img.getpixel((x, y)) != (255, 255, 255, 255):
                pixels_changed = True
                break
        if pixels_changed:
            break

    assert pixels_changed is True


def test_text_element_set_text():
    """Test updating text content."""
    elem = TextElement(position=(0, 0), text="Original", font_family="Open Sans", font_size=12)

    original_size = elem.get_size()

    elem.set_text_content("Much longer text string here")
    new_size = elem.get_size()

    # Width should increase with longer text
    assert new_size[0] > original_size[0]


# ==================== ImageElement Tests ====================


def test_image_element_initialization():
    """Test basic ImageElement initialization."""
    elem = ImageElement(position=(100, 50))

    assert elem.position == (100, 50)
    assert elem.image is None


def test_image_element_not_ready_without_image():
    """Test that ImageElement is not ready without image loaded."""
    elem = ImageElement(position=(0, 0))

    assert elem.is_ready() is False


def test_image_element_set_image():
    """Test loading image into ImageElement."""
    # Create a test image
    test_img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))

    elem = ImageElement(position=(0, 0))
    elem.set_image(test_img)

    assert elem.is_ready() is True
    assert elem.image is not None
    assert elem.image.size == (100, 100)


def test_image_element_get_size():
    """Test that ImageElement.get_size() returns image dimensions."""
    test_img = Image.new("RGBA", (150, 200), (255, 0, 0, 255))

    elem = ImageElement(position=(0, 0))
    elem.set_image(test_img)

    assert elem.get_size() == (150, 200)


def test_image_element_resize():
    """Test resizing ImageElement."""
    test_img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))

    elem = ImageElement(position=(0, 0), width=50, height=75)
    elem.set_image(test_img)

    assert elem.get_size() == (50, 75)


def test_image_element_draw():
    """Test that ImageElement.draw() pastes image."""
    test_img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))

    elem = ImageElement(position=(25, 25))
    elem.set_image(test_img)

    img = Image.new("RGB", (100, 100), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Check that red pixels were drawn
    center_pixel = img.getpixel((50, 50))
    assert center_pixel == (255, 0, 0)


# ==================== RectangleElement Tests ====================


def test_rectangle_element_initialization():
    """Test basic RectangleElement initialization."""
    elem = RectangleElement(position=(100, 50), width=200, height=150, fill="#FF0000")

    assert elem.position == (100, 50)
    assert elem.width == 200
    assert elem.height == 150
    assert elem.fill == (255, 0, 0, 255)


def test_rectangle_element_is_ready():
    """Test that RectangleElement is ready when dimensions are set."""
    elem = RectangleElement(position=(0, 0), width=100, height=50)

    assert elem.is_ready() is True


def test_rectangle_element_not_ready_without_dimensions():
    """Test that RectangleElement is not ready without width/height."""
    elem = RectangleElement(position=(0, 0))

    assert elem.is_ready() is False


def test_rectangle_element_get_size():
    """Test that RectangleElement.get_size() returns dimensions."""
    elem = RectangleElement(position=(0, 0), width=300, height=200)

    assert elem.get_size() == (300, 200)


def test_rectangle_element_draw_filled():
    """Test drawing a filled rectangle."""
    elem = RectangleElement(position=(10, 10), width=80, height=80, fill="#0000FF")

    img = Image.new("RGB", (100, 100), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Check that blue pixels were drawn
    center_pixel = img.getpixel((50, 50))
    assert center_pixel == (0, 0, 255)


def test_rectangle_element_draw_outline():
    """Test drawing a rectangle with outline."""
    elem = RectangleElement(position=(10, 10), width=80, height=80, outline="#FF0000", outline_width=2)

    img = Image.new("RGB", (100, 100), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Check that red outline was drawn
    edge_pixel = img.getpixel((10, 10))
    assert edge_pixel == (255, 0, 0)


def test_rectangle_element_rounded_corners():
    """Test drawing a rectangle with rounded corners."""
    elem = RectangleElement(position=(10, 10), width=80, height=80, fill="#00FF00", border_radius=10)

    img = Image.new("RGB", (100, 100), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Center should be green
    center_pixel = img.getpixel((50, 50))
    assert center_pixel == (0, 255, 0)


def test_rectangle_element_overlaps_region():
    """Test overlaps_region detection."""
    elem = RectangleElement(position=(50, 50), width=100, height=100)

    # Rectangle is at (50,50) to (150,150)
    assert elem.overlaps_region(0, 0, 100, 100) is True
    assert elem.overlaps_region(100, 100, 200, 200) is True
    assert elem.overlaps_region(0, 0, 200, 200) is True
    assert elem.overlaps_region(200, 200, 300, 300) is False


# ==================== EllipseElement Tests ====================


def test_ellipse_element_initialization():
    """Test basic EllipseElement initialization."""
    elem = EllipseElement(position=(100, 50), width=50, height=50, fill="#FF0000")

    assert elem.position == (100, 50)
    assert elem.width == 50
    assert elem.height == 50
    assert elem.fill == (255, 0, 0, 255)


def test_ellipse_element_is_ready():
    """Test that EllipseElement is ready when width and height are set."""
    elem = EllipseElement(position=(0, 0), width=100, height=100)

    assert elem.is_ready() is True


def test_ellipse_element_not_ready_without_dimensions():
    """Test that EllipseElement is not ready without width/height."""
    elem = EllipseElement(position=(0, 0))

    assert elem.is_ready() is False


def test_ellipse_element_get_size():
    """Test that EllipseElement.get_size() returns width and height."""
    elem = EllipseElement(position=(0, 0), width=100, height=100)

    assert elem.get_size() == (100, 100)


def test_ellipse_element_draw_filled():
    """Test drawing a filled ellipse."""
    elem = EllipseElement(position=(20, 20), width=60, height=60, fill="#0000FF")

    img = Image.new("RGB", (100, 100), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Center should be blue
    center_pixel = img.getpixel((50, 50))
    assert center_pixel == (0, 0, 255)


def test_ellipse_element_draw_outline():
    """Test drawing an ellipse with outline."""
    elem = EllipseElement(position=(20, 20), width=60, height=60, outline="#FF0000", outline_width=2)

    img = Image.new("RGB", (100, 100), "#FFFFFF")
    draw_ctx = ImageDraw.Draw(img)

    elem.draw(draw_ctx, img)

    # Check that red outline exists
    # Sample point on the ellipse edge
    edge_pixel = img.getpixel((50, 20))
    assert edge_pixel == (255, 0, 0)


def test_ellipse_element_overlaps_point():
    """Test overlaps_point detection using ellipse equation."""
    elem = EllipseElement(position=(25, 25), width=50, height=50)

    # Center point should overlap
    assert elem.overlaps_point(50, 50) is True

    # Point within ellipse should overlap
    assert elem.overlaps_point(60, 50) is True

    # Point outside ellipse should not overlap
    assert elem.overlaps_point(100, 50) is False


def test_ellipse_element_overlaps_region():
    """Test overlaps_region detection."""
    elem = EllipseElement(position=(25, 25), width=50, height=50)

    # Ellipse bounding box is (25,25) to (75,75)
    assert elem.overlaps_region(0, 0, 100, 100) is True
    assert elem.overlaps_region(40, 40, 60, 60) is True
    assert elem.overlaps_region(100, 100, 200, 200) is False


# ==================== Element Factory Integration ====================


def test_factory_create_text_element():
    """Test creating TextElement through factory."""
    factory = ElementFactory()
    elem = factory.create_element(
        "text", position=(10, 20), values={"text": "Test", "font_family": "Arial", "font_size": 14},
    )

    assert isinstance(elem, TextElement)
    assert elem.position == (10, 20)
    assert elem.text_content == "Test"


def test_factory_create_rectangle_element():
    """Test creating RectangleElement through factory."""
    factory = ElementFactory()
    elem = factory.create_element("rectangle", position=(5, 5), values={"width": 100, "height": 50, "fill": "#FF0000"})

    assert isinstance(elem, RectangleElement)
    assert elem.width == 100
    assert elem.height == 50


def test_factory_create_ellipse_element():
    """Test creating EllipseElement through factory."""
    factory = ElementFactory()
    elem = factory.create_element("ellipse", position=(50, 50), values={"width": 50, "height": 50, "fill": "#00FF00"})

    assert isinstance(elem, EllipseElement)
    assert elem.width == 50
    assert elem.height == 50


def test_factory_unknown_type_raises():
    """Test that unknown element type raises error."""
    factory = ElementFactory()

    with pytest.raises(ValueError, match="Unknown element type"):
        factory.create_element("unknown_type", position=(0, 0), values={})
