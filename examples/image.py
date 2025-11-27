from pathlib import Path
from poster_generator import Canvas, TextElement, ImageElement
from poster_generator.operations.image import apply_hue_shift

width = 1080
height = 1350

canvas = Canvas(width=width, height=height, background="#c75d5d")


background = ImageElement(
    (0, 0),
    image_path=Path.cwd() / "examples/assets/my_background.jpg",
    width=width,
    height=height,
)
background.apply_operation(lambda img: apply_hue_shift(img, 30))

canvas.add_element("background", background)


text_element = TextElement(
    (100, height//2 - 64),
    text="This time, with a background!",
    font_size=64,
    fill="#333333",
)
canvas.add_element("title", text_element)


image = canvas.render()
image.show()
