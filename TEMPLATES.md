# Poster Generator Templates

This document provides an in-depth overview of the template loaders that come with this library, supporting both YAML and JSON formats.

## Table of Contents
- [Overview](#overview)
- [Template Format](#template-format)
- [Variable Substitution](#variable-substitution)
- [Element Types](#element-types)
- [Positioning](#positioning)
- [Operations](#operations)
- [Custom Extensions](#custom-extensions)

---

## Overview

Templates allow you to define reusable poster layouts with variable substitution, making it easy to generate multiple variations from a single design. The library supports both YAML and JSON formats through `YamlLoader` and `JsonLoader`.

**Basic usage:**
```python
from poster_generator import YamlLoader

loader = YamlLoader()
canvas = loader.build_canvas("templates/basic.yml", variables={
    "hue_shift": 45,
    "title_text": "Hello, Poster Generator!",
    "background_image": "assets/my_background.jpg",
})
image = canvas.render()
```

---

## Template Format

Templates follow a consistent structure across both YAML and JSON formats:

```yaml
schema: "1.0"

settings:           # Canvas configuration
  width: 1080       # Canvas width in pixels
  height: 1350      # Canvas height in pixels
  background_color: "#f295df"  # Background color (hex or RGBA)

anchors:            # Optional: Named anchor points for positioning
  river:
    x: 350
    y: 275

layers:             # Layers organize elements (render bottom-to-top)
  background:
    settings:       # Optional layer settings
      opacity: 1.0
    elements:
      element_id:
        type: image
        position:
          x: 0
          y: 0
        values:
          # Element-specific properties
        operations:
          # Optional transformations
```

**Same structure in JSON:**
```json
{
  "schema": "1.0",
  "settings": {
    "width": 1080,
    "height": 1350,
    "background_color": "#000000"
  },
  "layers": {
    "background": {
      "elements": {
        "element_id": {
          "type": "image",
          "position": {"x": 0, "y": 0},
          "values": {}
        }
      }
    }
  }
}
```

---

## Variable Substitution

Use `--${variable_name}--` syntax to inject dynamic values into your templates:

**YAML example:**
```yaml
elements:
  title:
    type: text
    values:
      text: --${title_text}--
      font_size: --${size}--
      fill: --${color}--
```

**JSON example:**
```json
{
  "values": {
    "text": "--${title_text}--",
    "font_size": "--${size}--",
    "fill": "--${color}--"
  }
}
```

**Python usage:**
```python
canvas = loader.build_canvas("template.yml", variables={
    "title_text": "My Title",
    "size": 48,
    "color": "#FF0000"
})
```

Variables work with all value types: strings, numbers, colors, and nested structures.

---

## Element Types

### TextElement
**Type:** `text`

Renders text with custom fonts, wrapping, alignment, and styling.

**Properties:**
- `text` (str): Text content to render
- `font_size` (int): Font size in pixels
- `fill` (str|list): Text color as hex string or RGBA list
- `font_family` (str, optional): Font family name (see `get_font_manager().get_all_families()`)
- `max_width` (int, optional): Maximum width before wrapping
- `wrap_style` (str, optional): `'none'`, `'word'` (default), or `'char'`
- `text_alignment` (str, optional): `'left'` (default), `'center'`, or `'right'`

**Example (YAML):**
```yaml
title:
  type: text
  position: {x: 100, y: 100}
  values:
    text: "Hello, World!"
    font_size: 64
    fill: "#FFFFFF"
    font_family: "Open Sans"
    max_width: 400
    text_alignment: "center"
```

**Example (JSON):**
```json
{
  "title": {
    "type": "text",
    "rel_position": {
      "source": "alignment",
      "value": {"x": "center", "y": "center"}
    },
    "values": {
      "text": "--${title_text}--",
      "font_size": 56,
      "fill": "#bc4841",
      "max_width": 400,
      "text_alignment": "center"
    }
  }
}
```

### ImageElement
**Type:** `image`

Displays an image from a file path with optional resizing.

**Properties:**
- `image_path` (str): Path to the image file
- `width` (int, optional): Target width (resizes if provided)
- `height` (int, optional): Target height (resizes if provided)

**Example (YAML):**
```yaml
background:
  type: image
  position: {x: 0, y: 0}
  operations:
    apply_hue_shift:
      degrees: --${hue_shift}--
  values:
    image_path: --${background_image}--
    width: 1080
    height: 1350
```

### RectangleElement
**Type:** `rectangle`

Renders a rectangle with optional rounded corners, fill, and outline.

**Properties:**
- `width` (int): Rectangle width in pixels
- `height` (int): Rectangle height in pixels
- `fill` (str|list|dict): Fill color (hex, RGBA list, or RGB/RGBA dict)
- `outline` (str|list, optional): Outline color
- `outline_width` (int, optional): Outline thickness in pixels (default: 1)
- `border_radius` (int, optional): Corner radius for rounded corners (default: 0)

**Colors can be specified as:**
- Hex string: `"#FF5733"`
- RGBA list: `[255, 87, 51, 128]`
- RGBA dict: `{"red": 255, "green": 87, "blue": 51, "alpha": 128}`

**Example (JSON with semi-transparent fill):**
```json
{
  "main_panel": {
    "type": "rectangle",
    "rel_position": {
      "source": "alignment",
      "value": {"x": "center", "y": "center"}
    },
    "values": {
      "fill": {"red": 120, "blue": 200, "green": 120, "alpha": 20},
      "width": 650,
      "height": 750,
      "outline": [255, 255, 255, 110],
      "outline_width": 2,
      "border_radius": 10
    }
  }
}
```

### EllipseElement
**Type:** `ellipse`

Renders an ellipse or circle with fill and outline options.

**Properties:**
- `width` (int): Ellipse width in pixels
- `height` (int): Ellipse height in pixels (use same as width for a circle)
- `fill` (str|list|dict): Fill color
- `outline` (str|list, optional): Outline color
- `outline_width` (int, optional): Outline thickness in pixels

**Example (YAML):**
```yaml
circle:
  type: ellipse
  position: {x: 100, y: 100}
  values:
    width: 100
    height: 100
    fill: "#3498db"
    outline: "#2c3e50"
    outline_width: 3
```

---

## Positioning

Elements require either `position` or `rel_position`. Positioning is resolved during template loading.

### Absolute Positioning

**YAML:**
```yaml
position:
  x: 100
  y: 200
```

**JSON:**
```json
"position": {"x": 100, "y": 200}
```

### Relative Positioning

#### Anchor-based
Define anchors at the template root, then reference them:

```yaml
anchors:
  river:
    x: 350
    y: 275

layers:
  background:
    elements:
      title:
        rel_position:
          source: anchor
          value: river
          offset:
            x: 20
            y: 20
        # Resolves to position: (370, 295)
```

#### Element-based
Position relative to another element (must be defined first):

```yaml
subtitle:
  rel_position:
    source: element
    value: title1
    offset:
      x: 0
      y: 30
  # Positioned 30px below title1
```

#### Alignment-based
Use alignment keywords for positioning relative to canvas or parent element:

**JSON example:**
```json
{
  "rel_position": {
    "source": "alignment",
    "value": {"x": "center", "y": "center"}
  }
}
```

**With parent element:**
```json
{
  "rel_position": {
    "source": "alignment",
    "value": {"x": "50%", "y": "70%"},
    "parent": "main_panel",
    "offset": {"y": -20}
  }
}
```

**Supported alignment values:**
- `"center"` or `"50%"`: Center alignment
- `"10%"`, `"20%"`, etc.: Percentage-based positioning
- `"left"`, `"right"`, `"top"`, `"bottom"`: Edge alignment

---

## Operations

Operations allow you to transform elements during template loading. They're applied before rendering.

### Built-in Operations

#### For Images: `apply_hue_shift`
Shifts the hue of an image by a specified number of degrees.

**YAML:**
```yaml
operations:
  apply_hue_shift:
    degrees: 45
```

**JSON:**
```json
"operations": {
  "apply_hue_shift": {"degrees": 45}
}
```

#### For Images: `set_hue_from_hex`
Sets the hue based on a hex color value.

#### For Text: `randomize_text_color`
Randomizes the text color.

### Custom Operations

Register your own operations to extend functionality:

```python
from poster_generator.operations import register_operation

def uppercase_and_color(element, new_color):
    """Custom operation to uppercase text and change color."""
    element.text = element.text.upper()
    element.fill = new_color
    return element

# Register with a namespaced identifier
register_operation(
    "myapp.uppercase_and_color",
    uppercase_and_color,
    supported_types=["text"]
)
```

**Use in template:**
```yaml
operations:
  myapp.uppercase_and_color:
    new_color: "#f7e22f"
```

---

## Custom Extensions

### Custom Element Types

Create and register your own element types:

```python
from poster_generator.elements import DrawableElement, register_element_type

class CustomElement(DrawableElement):
    def __init__(self, position=(0, 0), custom_param=None):
        super().__init__(position)
        self.custom_param = custom_param
    
    def draw_composite(self, image_draw, image, **kwargs):
        # Your drawing logic here
        pass
    
    def is_ready(self):
        return self.position is not None
    
    def overlaps_region(self, x1, y1, x2, y2):
        # Implement overlap detection
        return False
    
    def get_size(self):
        return (100, 100)  # Return element dimensions

# Register for use in templates
register_element_type("custom", CustomElement)
```

**Use in template:**
```yaml
my_custom:
  type: custom
  position: {x: 100, y: 100}
  values:
    custom_param: "value"
```

### Custom Fonts

Register custom fonts for use in text elements:

```python
from poster_generator.elements.text import register_font_family

register_font_family("Super Feel", "assets/super_feel.ttf")
```

**Use in template:**
```yaml
special_text:
  type: text
  values:
    text: "Custom Font!"
    font_family: "Super Feel"
    font_size: 32
```

---

## Complete Example

Here's a full template demonstrating multiple features:

**advanced.json:**
```json
{
  "schema": "1.0",
  "settings": {
    "width": 1080,
    "height": 1350,
    "background_color": "#000000"
  },
  "layers": {
    "background": {
      "elements": {
        "photo_bg": {
          "type": "image",
          "position": {"x": 0, "y": 0},
          "values": {
            "image_path": "--${background_image}--",
            "width": 1080,
            "height": 1350
          }
        }
      }
    },
    "overlay_panel": {
      "elements": {
        "main_panel": {
          "type": "rectangle",
          "rel_position": {
            "source": "alignment",
            "value": {"x": "center", "y": "center"}
          },
          "values": {
            "fill": {"red": 120, "blue": 200, "green": 120, "alpha": 20},
            "width": 650,
            "height": 750,
            "outline": [255, 255, 255, 110],
            "outline_width": 2,
            "border_radius": 10
          }
        },
        "title_text": {
          "type": "text",
          "rel_position": {
            "source": "alignment",
            "value": {"x": "center", "y": "center"},
            "parent": "main_panel"
          },
          "values": {
            "text": "--${title_text}--",
            "font_size": 56,
            "fill": "#bc4841",
            "max_width": 400,
            "text_alignment": "center"
          }
        }
      }
    }
  }
}
```

**Python usage:**
```python
from poster_generator import JsonLoader

loader = JsonLoader()
canvas = loader.build_canvas("templates/advanced.json", variables={
    "background_image": "assets/my_background.jpg",
    "title_text": "Your Title Here"
})
image = canvas.render()
image.show()
```