from pathlib import Path

from poster_generator import Canvas, TextElement, RectangleElement
from poster_generator.operations.text import randomize_text_color
from poster_generator.utils import get_alignment_position

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

reg_text = TextElement(
    text="I'm regular!",
    font_size=32,
    fill="#333333",
)
canvas.add_element("reg_text", reg_text)
reg_text.align_to(x_align=0.5, y_align=0.4)

special_text = TextElement(
    position=(reg_text.position[0], reg_text.position[1] + 64),
    text="I'M SPECIAL!",
    font_size=32,
    fill="#5E174D",
    font_path=Path.cwd() / "examples/assets/super_feel.ttf",
    max_width=128,
    text_alignment="center"
)
special_text.apply_operation(randomize_text_color)
canvas.add_element("special_text", special_text)
special_text.update_position((reg_text.position[0], reg_text.position[1] + 64))

image = canvas.render()
image.show()
