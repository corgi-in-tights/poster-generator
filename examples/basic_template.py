from poster_generator import YamlLoader

template = "basic"
path = f"templates/{template}.yml"
print("Loading from:", path)

loader = YamlLoader()

variables = {
    "hue_shift": 45,
    "title_text": "Hello, Poster Generator!",
    "background_image": "assets/my_background.jpg",
}

canvas = loader.build_canvas(path, variables)

image = canvas.render()

image.show()
