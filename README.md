# Poster Generator

A *lightweight* flexible Python library for building and rendering graphics with support for layers, groups, and YAML-based templates.

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

	•	🧱 Layering system for Z-order control and basic blend settings leveraging [Pillow](https://python-pillow.org/)

	•	🗂️ Optional groups for quick categorization or batch selection

	•	📄 YAML templates with variable substitution for reusable layouts

	•	🎯 Anchors & relative positioning for layout-style placement

	•	🔌 Extensible, format-agnostic registry for custom elements and operations

	•	🛠️ Function-driven operations (e.g., hue shifting, scaling, transforms)
    
	•	📣 Designed for automated poster and social media generation

⸻


## Installation

### Using Poetry (recommended)

```bash
poetry add poster-generator
```

### Using pip

```bash
pip install poster-generator
```

### From source

```bash
git clone https://github.com/corgi-in-tights/poster-generator.git
cd poster-generator
poetry install
```

## Quick Start

### Programmatic Usage

Create a simple poster with text and image elements:

```python
from pathlib import Path
from poster_generator import Canvas, TextElement, ImageElement
from poster_generator.operations.image import apply_hue_shift

# Create a canvas
canvas = Canvas(width=1080, height=1350, background="#c75d5d")

# Add an image with hue shift
background = ImageElement(
    (0, 0),
    image_path="path/to/image.png",
    width=1080,
    height=1350,
)
background.apply_operation(lambda img: apply_hue_shift(img, 30))
canvas.add_element("background", background)

# Add text
text = TextElement(
    (50, height//2 - 64),
    text="Hello, Poster!",
    font_size=64,
    color="#333333",
)
canvas.add_element("title", text)

# Render and save
image = canvas.render()
image.save("output.png")
```

### YAML Template Usage

Define your poster in a YAML template:

```yaml
---
schema: "1.0"
settings:
  width: 1080
  height: 1350
  background_color: "#f295df"

anchors:
  top_left:
    x: 50
    y: 50

layers:
  background:
    settings:
      opacity: 1.0
    elements:
      bg_image:
        type: image
        position: [0, 0]
        operations:
          apply_hue_shift:
            degrees: --${hue_shift}--
        values:
          image_path: --${background_image}--
          width: 1080
          height: 1350
    
  text:
    elements:
      title:
        type: text
        rel_position:
          source: anchor
          id: top_left
        values:
          text: --${title_text}--
          font_size: 64
          color: "#FFFFFF"

      subtitle:
        type: text
        rel_position:
          source: element
          id: title
          offset:
            x: 0
            y: 50
        values:
          text: My subtitle :)
          font_size: 30
          color: "#FFFFFF"
```

Load and render the template:

```python
from poster_generator.loaders import YamlLoader

loader = YamlLoader()
canvas = loader.build_canvas(
    "template.yml",
    variables={
        "hue_shift": 45,
        "title_text": "My Poster",
        "background_image": "background.png",
    }
)

image = canvas.render()
image.save("output.png")
```

## Core Concepts

### Canvas

The `Canvas` is the main container for your poster. It manages elements, layers, and rendering.

```python
canvas = Canvas(width=1080, height=1350, background="#ffffff")
```

### Elements

Elements are the building blocks of your poster:

- **TextElement**: Renders text with custom styling
- **ImageElement**: Renders images with transformation support

```python
# Text element
text = TextElement(
    position=(100, 100),
    text="Hello World",
    font_size=48,
    color="#000000"
)

# Image element
image = ImageElement(
    position=(0, 0),
    image_path="image.png",
    width=500,
    height=500
)
```

### Layers

Layers help organize elements and control rendering order:

```python
canvas.add_element("bg", background, layer="background")
canvas.add_element("title", text, layer="foreground")
```

### Groups

Groups allow you to manage related elements:

```python
canvas.add_element("title", text, groups=["headers", "top-section"])
canvas.add_element("subtitle", subtitle, groups=["headers", "top-section"])

# Query elements by group
headers = canvas.get_elements(groups="headers")
```

### Operations

Apply transformations to elements:

```python
from poster_generator.operations.image import apply_hue_shift, set_hue_from_hex

# Hue shift
element.apply_operation(lambda img: apply_hue_shift(img, degrees=45))

# Set hue from color
element.apply_operation(lambda img: set_hue_from_hex(img, "#FF5733"))
```

## Advanced Usage

### Custom Element Types

Register your own element types using the factory pattern:

```python
from poster_generator.elements import DrawableElement, register_element_type

class CustomElement(DrawableElement):
    def __init__(self, position, custom_param=None):
        super().__init__(position)
        self.custom_param = custom_param
    
    def draw(self, draw, image, blend_settings: dict):
        # Your drawing logic
        pass
    
    def is_ready(self):
        return True
    
    def overlaps_region(self, x1, y1, x2, y2):
        return False
    
    def apply_operation(self, operation):
        pass

# Register the custom element
register_element_type("custom", CustomElement)
```

### Element Queries

Query elements by identifier, group, or layer:

```python
# Get specific elements
elements = canvas.get_elements(identifiers=["title", "subtitle"])

# Get by group
headers = canvas.get_elements(groups="headers")

# Get by layer
bg_elements = canvas.get_elements(layers="background")

# Combine filters (require all)
specific = canvas.get_elements(
    groups="headers",
    layers="foreground",
    require_all=True
)
```

### YAML Variable Substitution

Use `--${variable_name}--` syntax in YAML templates:

```yaml
values:
  text: --${title}--
  font_size: --${size}--
  color: --${color}--
```

```python
canvas = loader.build_canvas(
    "template.yml",
    variables={
        "title": "My Title",
        "size": 48,
        "color": "#FF0000"
    }
)
```

### Relative Positioning

Position elements relative to anchors or other elements:

```yaml
# Relative to anchor
rel_position:
  source: anchor
  id: top_left
  offset:
    x: 20
    y: 30

# Relative to another element
rel_position:
  source: element
  id: title
  offset:
    x: 0
    y: 50
```

## API Reference

### Canvas

- `Canvas(width, height, background)` - Create a new canvas with specified dimensions and background color
- `add_element(identifier, element, groups=None, layer="default")` - Add an element to the canvas with a unique identifier, optional groups, and layer assignment
- `remove_element(identifier)` - Remove an element from the canvas by its identifier
- `get_elements(identifiers=None, groups=None, layers=None, require_all=False)` - Query and retrieve elements by identifiers, groups, or layers. Set `require_all=True` to match all criteria
- `clear_layer(layer)` - Clear all elements from a specific layer
- `clear_group(group)` - Clear all elements belonging to a specific group
- `crop(x1, y1, x2, y2)` - Crop the canvas to the rectangular region defined by coordinates (x1, y1) as top-left and (x2, y2) as bottom-right
- `align_element(identifier, x_align, y_align)` - Set an element's position to a specific canvas-based alignment (e.g., 'center', 'left', 'right', 'top', 'bottom')
- `render(global_op=None)` - Render the canvas to an image, optionally applying global operations
- `from_dict(data)` - Create and populate a canvas from a dictionary representation

### TextElement

- `TextElement(position, text=None, font_path=None, font_size=20, color="#000")` - Create text element
- `draw(draw, image, position=None)` - Draw the text
- `is_ready()` - Check if ready to render

### ImageElement

- `ImageElement(position, image_path=None, width=None, height=None)` - Create image element
- `load_image(image_path)` - Load an image file
- `apply_hue_shift(degrees)` - Shift image hue
- `set_hue_from_hex(hex_color)` - Set hue from color
- `apply_operation(operation)` - Apply transformation
- `draw(draw, canvas_image, position=None)` - Draw the image
- `is_ready()` - Check if ready to render

### YamlLoader

- `YamlLoader()` - Create YAML loader
- `build_canvas(source, variables=None)` - Build canvas from YAML file or dict

## Examples

Check out the `examples/` directory for more complete examples:

- `examples/basic.py` - Programmatic poster creation
- `examples/yml.py` - YAML template loading
- `examples/templates/my_template.yml` - Example YAML template

## Requirements

- Python >= 3.13
- Pillow >= 12.0.0
- PyYAML >= 6.0.3

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/corgi-in-tights/poster-generator.git
cd poster-generator

# Install dependencies
poetry install

# Run examples
poetry run python examples/basic.py
poetry run python examples/yml.py
```

### Project Structure

```
poster_generator/
├── ...
├── canvas.py              # Canvas class
├── elements/              # Element implementations
│   ├── drawable.py        # Base element class
│   ├── text.py            # Text element
│   ├── image.py           # Image element
│   └── factory.py         # Element factory
├── loaders/               # Template loaders
│   ├── base.py            # Base loader
│   └── yaml_loader.py     # YAML loader
└── operations/            # Image operations
    ├── ...
    └── factory.py         # Operation factory
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. I am open to significant design changes if they match the project's intention.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Issues

I cannot guarantee this project will be actively maintained since there really isn't much to add from my end. The current end product fulfills my rather primitive needs -- however, if any critical bugs come up, please open a GitHub issue. 

If there are architectural issues (i.e. inflexible code), then please feel free to open an issue, but for additional features, a PR would be much preferred.

## Acknowledgments

- Built with [Pillow](https://python-pillow.org/) for image processing
- Uses [PyYAML](https://pyyaml.org/) for template parsing (by default)
- This project and README was partially built with the help of Claude, though all architectural decisions are fully my own.