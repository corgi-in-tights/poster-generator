from pathlib import Path
from poster_generator import Canvas, TextElement, ImageElement
from poster_generator.operations.image import apply_hue_shift

if __name__ == "__main__":
    width = 1080
    height = 1350
    
    canvas = Canvas(width=width, height=height, background="#c75d5d")

    background = ImageElement(
        (0, 0),
        image_path=Path.cwd() / "examples/assets/bg.png",
        width=width,
        height=height,
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

    image = canvas.render()
    image.show()
