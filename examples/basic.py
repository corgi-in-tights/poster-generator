from pathlib import Path
from poster_generator import Canvas, TextElement, ImageElement
from poster_generator.operations.image import apply_hue_shift

SIZE = (1080, 1350)

if __name__ == "__main__":
    canvas = Canvas(width=SIZE[0], height=SIZE[1], background="#c75d5d")

    background = ImageElement(
        (0, 0),
        image_path=Path.cwd() / "examples/assets/bg.png",
        width=SIZE[0],
        height=SIZE[1],
    )
    background.apply_operation(lambda img: apply_hue_shift(img, 30))

    canvas.add_element("background", background)

    text_element = TextElement(
        (50, 50),
        text="Hello, Poster!",
        font_size=200,
        color="#333333",
    )
    canvas.add_element("title", text_element)

    # canvas.remove_element("title")

    image = canvas.render()
    image.show()
    # image.save(abspath("output.png"))
