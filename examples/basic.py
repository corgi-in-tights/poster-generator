from pathlib import Path
from poster_generator import Canvas, TextElement, ImageElement
from poster_generator.operations.image import apply_hue_shift
from poster_generator.loaders import YamlLoader

SIZE = (1080, 1350)
CWD = Path(__file__).parent

def abspath(s):
    return CWD / s

if __name__ == "__main__":
    canvas = Canvas(size=SIZE, background="#ffffff")

    background = ImageElement(
        image_path=abspath("bg.png"),
        position=(0, 0),
        size=SIZE
    )
    background.apply_operation(lambda img: apply_hue_shift(img, 30))
    
    canvas.add_element("background", background)


    text_element = TextElement(
        text="Hello, Poster!",
        font_size=200,
        color="#333333", 
        position=(50, 50)
    )
    canvas.add_element("title", text_element)


    image = canvas.render()
    image.show()
    image.save(abspath("output.png"))
