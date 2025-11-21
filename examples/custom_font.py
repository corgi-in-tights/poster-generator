from pathlib import Path
from poster_generator import Canvas, TextElement
from poster_generator.operations.text import randomize_text_color

width = 512
height = 512

canvas = Canvas(width=width, height=height, background="#6f8662")

reg_text = TextElement(
    None,
    text="I'm regular!",
    font_size=32,
    color="#333333",
)
reg_text.update_position(canvas.get_alignment_position(reg_text, x_align="center", y_align="center"))
reg_text.translate(0, -64)
canvas.add_element("reg_text", reg_text)

special_text = TextElement(
    (reg_text.position[0], reg_text.position[1] + 64),
    text="I'M SPECIAL!",
    font_size=32,
    color="#5E174D",
    font_path=Path.cwd() / "examples/assets/super_feel.ttf",
    max_width=128,
    text_alignment="center"
)
special_text.apply_operation(randomize_text_color)
canvas.add_element("special_text", special_text)

image = canvas.render()
image.show()
