from pathlib import Path
from poster_generator import JsonLoader

template = "advanced"
path = f"examples/templates/{template}.json"
print("Loading from:", path)

loader = JsonLoader()

variables = {
    "background_image": "assets/my_background.jpg",
    "tagline_text": "Your Tagline Here",
    "title_text": "Your Title Here",
    "details_text": "Additional details here"
}

canvas = loader.build_canvas(path, variables)

image = canvas.render()

image.show()
