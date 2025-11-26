# Poster Generator Templates

This file is an in-depth overview of the in-built YAML template loader that comes with this library.

### Format

```yaml
schema: "1.0"

settings: # Canvas settings
  width: # Canvas width, default 1080
  height: # Canvas height, default 1350
  background_color: # Background color

anchors: # Optional anchors for relative positioning

layers:
  MY_LAYER_NAME:
    settings: # Optional layer-related & blend settings, currently only opacity
      opacity: # Optional opacity 0.0 to 1.0
    elements:
      MY_ELEMENT_ID:
        type: # rectangle | circle | image | text | etc.
        position: # or rel_position, atleast one is mandatory
          ...
        values:
          ...
        operations: # optional
          ...
  MY_OTHER_LAYER:
    ...
```


Example templates:
```yaml
schema: "1.0"
settings:
  width: 1080
  height: 1350
  background_color: "#f295df"
anchors:
  river:
    x: 350
    y: 275
layers:
  background:
    elements:
      partitioned_thing:
        type: rectangle
        position:
          x: 50
          y: 50
        operations:
          apply_hue_shift:
            degrees: --${hue_shift}--
        values:
          image_path: --${background_image}--
          width: 980
          height: 1250
      title1:
        type: text
        groups:
          - top-left
          - headers
        rel_position:
          source: anchor
          value: river
          offset:
            x: 20
            y: 20
        values:
          text: --${title_text}--
          font_size: 32
          color: "#FFFFFF"
      subtitle1:
        type: text
        groups:
          - top-left
          - subheaders
        rel_position:
          source: element
          value: title1
          offset:
            x: 0
            y: 30
        values:
          text: My subtitle :)
          font_size: 24
          color: "#fff"
```
TODO: Output Image



```yaml
schema: "1.0"
settings:
  width: 512
  height: 512
  background_color: "#fff"
layers:
  background:
    elements:
      full_bg:
        type: image
        position:
          x: 0
          y: 0
        operations:
          apply_hue_shift:
            degrees: --${hue_shift}--
        values:
          image_path: --${background_image}--
          width: 1080
          height: 1350
      title1:
        type: text
        groups:
          - top-left
          - headers
        rel_position:
          source: anchor
          value: river
          offset:
            x: 20
            y: 20
        values:
          text: --${title_text}--
          font_size: 32
          color: "#FFFFFF"
      subtitle1:
        type: text
        groups:
          - top-left
          - subheaders
        rel_position:
          source: element
          value: title1
          offset:
            x: 0
            y: 30
        values:
          text: My subtitle :)
          font_size: 24
          color: "#FFFFFF"
```
TODO: Output Image


### YAML Variable Substitution

Almost every (key: constant) mapping supports variable substitution, from colors to all numbers.

Use `--${variable_name}--` syntax in YAML templates:

```yaml
values:
  text: --${title}--
  font_size: --${size}--
  color: --${color}--
```

Then when loading the canvas, pass in the variables by the mapping:

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


### Element Reference
Each element is defined as such:
```yaml
layers:
  my_layer:
    ELEMENT_ID:
      type: text # refers to text | image | etc.
      position: # either this or rel_position are required
        x: 0 
        y: 0
      groups: # optional, denote a list of groups, useful for operations
        - my-background-elements
      values: # kwargs to be passed for the element
      - text: This is a text box!
    ELEMENT_ID2:
      ...
```

### RectangleElement
"type: rectangle"
- width: Rectangle width in pixels
- height: Rectangle height in pixels
- background: Background color as hex string (e.g., "#FF5733")
- outline_color: Outline color as hex string, or None for no outline
- outline_width: Width of the outline in pixels
- radius: Corner radius in pixels for rounded corners (0 for sharp corners)


### CircleElement
"type: circle"
- radius: Circle radius in pixels.
- background: background color as hex string (e.g., "#FF5733").
- outline_color: Outline color as hex string, or None for no outline.
- outline_width: Width of the outline in pixels.

  
### TextElement
"type: text"
- text: A string containing what you want to be rendered
- font_size: Size of text in pixels
- font_path: Absolute path to .ttf containing font
- color: Text color
- max_width: None by default, if provided, wraps the word if curr_width > max_width
- wrap_style: Either 'none', 'word' (default), 'char'. Wraps the sentence IF max_width is provided
- text_alignment: Either 'left' (default), 'center', or 'right'. Aligns text content in bbox
- other_kwargs: Mapping of arbitrary key: values passed to Pillow's `ImageDraw.Draw()`. For advanced users only

All values above are provided to operations.

The following text operations are provided by default:
- randomize_text_color


### ImageElement
"type: image"
- image_path: Absolute path to image file to be displayed
- width: no resize by default, set image width in px
- height: no resize by default, set image height in px

All values above are provided to operations including element.image which refers to the image that will be pasted at element.position.

The following text operations are provided by default:
- apply_hue_shift
- set_hue_from_hex

### Element Operations

The element template accepts arbitrary function operations which can be used to apply conditional logic:

```yaml
MY_ELEMENT:
  type: image
  position:
    x: 0
    y: 0
  operations:
    apply_hue_shift:
      degrees: --${hue_shift}--
  values:
    image_path: --${background_image}--
    width: 1080
    height: 1350
```

`hue_shift` is an in-built operation that shifts the hue by a certain amount of degrees, passed in as a variable.


Custom operations can be made like so:

```python
from poster_generator.operations import register_operation

def uppercase_and_color(text_obj, new_color):
    text_obj["text"] = text_obj["text"].upper()
    text_obj["color"] = new_color
    return text_obj

# Register to operation factory
register_operation(
    "mynamespace.uppercase_and_color", # Recommended to attach a namespace!
    uppercase_and_color,
    supported_types=["text"]
)

# Then render the template like normal
```
```yaml
operations:
  mynamespace.uppercase_and_color:
    new_color: "#f7e22f"
```



### Relative Positioning

Relative positioning is done at a high-level, i.e. during the loading time, keeping the code simple but the template logic more advanced. Either `position` or `rel_position` are *required* for all element types. The offset key is optional and defaults to (0, 0).

Rel. positions can be done relative to anchors which are defined in their own element like so:
```yaml
anchors:
  river:
    x: 350
    y: 275

layers:
  my_layer:
    my_element:
      ...
      rel_position:
        source: anchor
        value: top_left
        offset:
          x: 20
          y: 30
      # resolves to: position: (370, 305)
```

Or to another element -- which must have been defined *before* this element.

```yaml
# Relative to another element
rel_position:
  source: element
  value: my_element_identifier
  offset:
    x: 0
    y: 10
```



