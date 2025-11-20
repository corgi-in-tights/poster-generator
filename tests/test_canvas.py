from poster_generator.canvas import Canvas
import random


class StubElement:
    """
    Minimal fake element for testing Canvas behavior.
    """

    def __init__(self, ready=True):
        self.ready = ready
        self.drawn = False  # track draw calls
        self.position = (0, 0)

    def is_ready(self):
        return self.ready

    def draw(self, draw_ctx, image, blend_settings=None):
        self.drawn = True

    def overlaps_region(self, x1, y1, x2, y2):
        # Simple rule: element at 0,0 overlaps only if crop includes origin
        return x1 <= 0 <= x2 and y1 <= 0 <= y2


def test_canvas_initialization():
    canvas = Canvas(width=400, height=300, background="#000")
    assert canvas.width == 400
    assert canvas.height == 300
    assert canvas.background == "#000"
    assert canvas.elements == {}
    assert canvas.layers == {}
    assert canvas.groups == {}


def test_add_and_query_element():
    canvas = Canvas()
    elem = StubElement()

    canvas.add_element("title", elem, groups=["text"], layer="foreground")

    assert "title" in canvas.elements
    assert "foreground" in canvas.layers
    assert canvas.layers["foreground"]["elements"] == ["title"]
    assert "text" in canvas.groups
    assert "title" in canvas.groups["text"]

    # Query by group
    results = canvas.get_elements(groups="text")
    assert results == [elem]


def test_remove_element():
    canvas = Canvas()
    elem = StubElement()
    canvas.add_element("item", elem, groups=["test"], layer="main")

    canvas.remove_element("item")

    assert "item" not in canvas.elements
    assert "item" not in canvas.groups["test"]
    assert canvas.layers["main"]["elements"] == []


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


def test_crop_removes_out_of_bounds_elements():
    canvas = Canvas()

    inside = StubElement()
    outside = StubElement()

    # inside element overlaps (0,0)
    canvas.add_element("in", inside)
    # outside never overlaps region
    outside.overlaps_region = lambda *_: False
    canvas.add_element("out", outside)

    canvas.crop(0, 0, 100, 100)

    assert "in" in canvas.elements
    assert "out" not in canvas.elements

def test_basic_rendering():
    width = 512
    height = 512

    canvas = Canvas(width=width, height=height, background="#148640")

    image = canvas.render()

    assert image.size == (512, 512)
    
    random.seed(42)
    for _ in range(10):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        assert image.getpixel((x, y)) == (20, 134, 64)