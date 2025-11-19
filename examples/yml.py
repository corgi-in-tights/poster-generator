from pathlib import Path
from poster_generator.loaders import YamlLoader


if __name__ == "__main__":
    path = str(Path.cwd() / "examples/templates/my_template.yml")
    print("Loading from:", path)

    loader = YamlLoader()

    variables = {
        "hue_shift": 45,
        "title_text": "Hello, Poster Generator!",
        "background_image": str(Path.cwd() / "examples/assets/my_background.png"),
    }

    canvas = loader.build_canvas(path, variables)
    
    image = canvas.render()
    
    image.show()
