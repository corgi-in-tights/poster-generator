# ruff: noqa: PLR2004, INP001
"""Tests for Canvas element management and rendering."""

import pytest

from poster_generator.canvas import Canvas


class StubElement:
    """
    Minimal fake element for testing Canvas behavior.
    """

    def __init__(self, *, ready=True, position=(0, 0), width=10, height=10):
        self.ready = ready
        self.drawn = False  # track draw calls
        self.position = position
        self.width = width
        self.height = height

    def is_ready(self):
        return self.ready

    def draw(self, draw_ctx, image, blend_settings=None):
        self.drawn = True

    def overlaps_region(self, x1, y1, x2, y2):
        # Element overlaps if any part of its bounding box intersects the region
        ex1, ey1 = self.position
        ex2 = ex1 + self.width
        ey2 = ey1 + self.height
        return not (ex2 < x1 or ex1 > x2 or ey2 < y1 or ey1 > y2)

    def get_size(self):
        return (self.width, self.height)

    def update_position(self, position):
        self.position = position

    def translate(self, dx, dy):
        self.position = (self.position[0] + dx, self.position[1] + dy)

    def bind_canvas(self, canvas, identifier):
        self._identifier = identifier
        self._canvas = canvas

# ==================== Canvas Creation ====================


def test_canvas_initialization():
    canvas = Canvas(width=400, height=300, background="#000")
    assert canvas.width == 400
    assert canvas.height == 300
    assert canvas.background == "#000"
    assert canvas.elements == {}
    assert canvas.layers == {}
    assert canvas.groups == {}


def test_canvas_from_dict():
    data = {"width": 1920, "height": 1080, "background": "#123456"}
    canvas = Canvas.from_dict(data)

    assert canvas.width == 1920
    assert canvas.height == 1080
    assert canvas.background == "#123456"


def test_canvas_defaults():
    canvas = Canvas()
    assert canvas.width == 1080
    assert canvas.height == 1350
    assert canvas.background == "#fff"


# ==================== Adding Elements ====================


def test_add_element_basic():
    canvas = Canvas()
    elem = StubElement()

    canvas.add_element("title", elem)

    assert "title" in canvas.elements
    assert canvas.elements["title"] is elem


def test_add_element_with_layer():
    canvas = Canvas()
    elem = StubElement()

    canvas.add_element("title", elem, layer="foreground")

    assert "foreground" in canvas.layers
    assert "title" in canvas.layers["foreground"]["elements"]


def test_add_element_with_groups():
    canvas = Canvas()
    elem = StubElement()

    canvas.add_element("title", elem, groups=["text", "headers"])

    assert "text" in canvas.groups
    assert "headers" in canvas.groups
    assert "title" in canvas.groups["text"]
    assert "title" in canvas.groups["headers"]


def test_add_element_with_layer_and_groups():
    canvas = Canvas()
    elem = StubElement()

    canvas.add_element("title", elem, groups=["text"], layer="foreground")

    assert "title" in canvas.elements
    assert "foreground" in canvas.layers
    assert canvas.layers["foreground"]["elements"] == ["title"]
    assert "text" in canvas.groups
    assert "title" in canvas.groups["text"]


def test_add_element_duplicate_identifier_raises():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()

    canvas.add_element("title", elem1)

    with pytest.raises(ValueError, match="Element with identifier 'title' already exists"):
        canvas.add_element("title", elem2)


def test_add_multiple_elements():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    elem3 = StubElement()

    canvas.add_element("elem1", elem1, layer="background")
    canvas.add_element("elem2", elem2, layer="foreground")
    canvas.add_element("elem3", elem3, layer="foreground")

    assert len(canvas.elements) == 3
    assert len(canvas.layers["foreground"]["elements"]) == 2


# ==================== Removing Elements ====================


def test_remove_element_basic():
    canvas = Canvas()
    elem = StubElement()
    canvas.add_element("item", elem)

    canvas.remove_element("item")

    assert "item" not in canvas.elements


def test_remove_element_from_layer():
    canvas = Canvas()
    elem = StubElement()
    canvas.add_element("item", elem, layer="main")

    canvas.remove_element("item")

    assert "item" not in canvas.elements
    assert "item" not in canvas.layers["main"]["elements"]


def test_remove_element_from_groups():
    canvas = Canvas()
    elem = StubElement()
    canvas.add_element("item", elem, groups=["test", "sample"])

    canvas.remove_element("item")

    assert "item" not in canvas.elements
    assert "item" not in canvas.groups["test"]
    assert "item" not in canvas.groups["sample"]


def test_remove_element_nonexistent():
    canvas = Canvas()
    # Should not raise
    canvas.remove_element("nonexistent")


def test_remove_multiple_elements():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    canvas.add_element("elem1", elem1)
    canvas.add_element("elem2", elem2)

    canvas.remove_elements(["elem1", "elem2"])

    assert "elem1" not in canvas.elements
    assert "elem2" not in canvas.elements


def test_clear_layer():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    elem3 = StubElement()

    canvas.add_element("e1", elem1, layer="layer1")
    canvas.add_element("e2", elem2, layer="layer1")
    canvas.add_element("e3", elem3, layer="layer2")

    canvas.clear_layer("layer1")

    assert "e1" not in canvas.elements
    assert "e2" not in canvas.elements
    assert "e3" in canvas.elements
    assert "layer1" not in canvas.layers


def test_clear_group():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    elem3 = StubElement()

    canvas.add_element("e1", elem1, groups=["group1"])
    canvas.add_element("e2", elem2, groups=["group1"])
    canvas.add_element("e3", elem3, groups=["group2"])

    canvas.clear_group("group1")

    assert "e1" not in canvas.elements
    assert "e2" not in canvas.elements
    assert "e3" in canvas.elements
    assert "group1" not in canvas.groups


# ==================== Getting/Querying Elements ====================


def test_get_elements_by_identifier():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    canvas.add_element("elem1", elem1)
    canvas.add_element("elem2", elem2)

    results = canvas.get_elements(identifiers="elem1")

    assert results == [elem1]


def test_get_elements_by_multiple_identifiers():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    elem3 = StubElement()
    canvas.add_element("elem1", elem1)
    canvas.add_element("elem2", elem2)
    canvas.add_element("elem3", elem3)

    results = canvas.get_elements(identifiers=["elem1", "elem3"])

    assert set(results) == {elem1, elem3}


def test_get_elements_by_group():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    canvas.add_element("e1", elem1, groups=["text"])
    canvas.add_element("e2", elem2, groups=["images"])

    results = canvas.get_elements(groups="text")

    assert results == [elem1]


def test_get_elements_by_layer():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    canvas.add_element("e1", elem1, layer="foreground")
    canvas.add_element("e2", elem2, layer="background")

    results = canvas.get_elements(layers="foreground")

    assert results == [elem1]


def test_get_elements_multiple_filters_any():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    elem3 = StubElement()
    canvas.add_element("e1", elem1, groups=["text"], layer="foreground")
    canvas.add_element("e2", elem2, groups=["images"], layer="foreground")
    canvas.add_element("e3", elem3, groups=["text"], layer="background")

    # Should get elements matching ANY condition
    results = canvas.get_elements(groups="text", layers="foreground", require_all=False)

    assert set(results) == {elem1, elem2, elem3}


def test_get_elements_multiple_filters_all():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    elem3 = StubElement()
    canvas.add_element("e1", elem1, groups=["text"], layer="foreground")
    canvas.add_element("e2", elem2, groups=["images"], layer="foreground")
    canvas.add_element("e3", elem3, groups=["text"], layer="background")

    # Should get elements matching ALL conditions
    results = canvas.get_elements(groups="text", layers="foreground", require_all=True)

    assert results == [elem1]


def test_get_elements_no_filters_returns_all():
    canvas = Canvas()
    elem1 = StubElement()
    elem2 = StubElement()
    canvas.add_element("e1", elem1)
    canvas.add_element("e2", elem2)

    results = canvas.get_elements()

    assert set(results) == {elem1, elem2}


def test_get_first_element():
    canvas = Canvas()
    elem = StubElement()
    canvas.add_element("test", elem)

    result = canvas.get_first_element(identifier="test")

    assert result is elem


def test_get_first_element_not_found():
    canvas = Canvas()

    result = canvas.get_first_element(identifier="nonexistent")

    assert result is None


# ==================== Rendering ====================


def test_render_calls_draw_on_ready_elements():
    canvas = Canvas()
    elem = StubElement(ready=True)
    canvas.add_element("a", elem)

    image = canvas.render()

    assert elem.drawn is True
    assert image is not None


def test_render_skips_not_ready_elements():
    canvas = Canvas()
    elem = StubElement(ready=False)
    canvas.add_element("a", elem)

    image = canvas.render()

    assert elem.drawn is False
    assert image is not None


def test_render_returns_image():
    canvas = Canvas(width=512, height=512)
    image = canvas.render()

    assert image.size == (512, 512)


def test_render_background_color():
    width = 512
    height = 512
    canvas = Canvas(width=width, height=height, background="#148640")

    image = canvas.render()

    assert image.size == (512, 512)
    # Check center and corners for background color
    assert image.getpixel((256, 256)) == (20, 134, 64)
    assert image.getpixel((0, 0)) == (20, 134, 64)
    assert image.getpixel((511, 511)) == (20, 134, 64)


# ==================== Cropping ====================


def test_crop_removes_out_of_bounds_elements():
    canvas = Canvas()

    inside = StubElement(position=(10, 10))
    outside = StubElement(position=(200, 200))

    canvas.add_element("in", inside)
    canvas.add_element("out", outside)

    canvas.crop(0, 0, 100, 100)

    assert "in" in canvas.elements
    assert "out" not in canvas.elements


def test_crop_keeps_partially_overlapping_elements():
    canvas = Canvas()

    elem = StubElement(position=(90, 90), width=20, height=20)
    canvas.add_element("partial", elem)

    canvas.crop(0, 0, 100, 100)

    assert "partial" in canvas.elements


# ==================== Element Translation ====================


def test_element_translate():
    elem = StubElement(position=(50, 50))

    elem.translate(10, 20)

    assert elem.position == (60, 70)


def test_element_translate_negative():
    elem = StubElement(position=(100, 100))

    elem.translate(-20, -30)

    assert elem.position == (80, 70)


def test_element_update_position():
    elem = StubElement(position=(0, 0))

    elem.update_position((100, 200))

    assert elem.position == (100, 200)
