from pathlib import Path
from poster_generator.loaders import YamlLoader


if __name__ == "__main__":
    path = str(Path.cwd() / "examples/grid.yml")
    print("Loading from:", path)
    
    loader = YamlLoader()
    
    print(loader.build_canvas(
        path,
        {
            "hue_shift": 45,
            "title_text": "Hello, Poster Generator!",
        }
    ))