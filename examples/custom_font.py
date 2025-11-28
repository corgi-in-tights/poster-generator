import random
from pathlib import Path

from poster_generator import Canvas, TextElement, RectangleElement
from poster_generator.operations import randomize_text_color
from poster_generator.elements.text import get_font_manager, register_font_family


width = 512
height = 512

canvas = Canvas(width=width, height=height, background="#6f8662")

bg = RectangleElement(
    width=width-128,
    height=height-128,
    fill="#4B5D4D",
    border_radius=16,
)
canvas.add_element("bg", bg)
# Align to should be called *after* being bound to the canvas or pass in the canvas= arg
# This is for width/height calculations
bg.align_to(x_align=0.5, y_align=0.5)


random_text = TextElement(
    text="I'm random!",
    font_size=32,
    fill="#333333",
    font_family=random.choice(get_font_manager().get_all_families()),
)
canvas.add_element("random_text", random_text)
random_text.align_to(x_align=0.5, y_align=0.4)


register_font_family("Super Feel", Path.cwd() / "examples/assets/super_feel.ttf")

special_text = TextElement(
    position=(random_text.position[0], random_text.position[1] + 64),
    text="I'M SPECIAL!",
    font_size=32,
    fill="#5E174D",
    font_family="Super Feel",
    max_width=128,
    text_alignment="center"
)
special_text.apply_operation(randomize_text_color)
canvas.add_element("special_text", special_text)
special_text.update_position((random_text.position[0], random_text.position[1] + 64))

image = canvas.render()
image.show()
