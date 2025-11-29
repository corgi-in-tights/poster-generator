from poster_generator import YamlLoader

template = "poster"
path = f"templates/{template}.yml"
print("Loading from:", path)

loader = YamlLoader()

variables = {
    "background_image": "assets/my_background.jpg",
    "tagline_text": "Your Tagline Here",
    "title_text": "Your Title Here",
    "details_text": "Additional details here"
}

canvas = loader.build_canvas(path, variables)

image = canvas.render()

image.show()
