from pathlib import Path
from poster_generator.loaders import YamlLoader

template = "advanced"
path = str(Path.cwd() / f"examples/templates/{template}.yml")
print("Loading from:", path)

loader = YamlLoader()

variables = {
    "background_image": str(Path.cwd() / "examples/assets/my_background.jpg"),
    "tagline_text": "Your Tagline Here",
    "title_text": "Your Title Here",
    "details_text": "Additional details here"
}

canvas = loader.build_canvas(path, variables)

image = canvas.render()

image.show()
