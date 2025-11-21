# Poster Generator Templates

## YAML

Example templates:
```yaml
---
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
    settings:
      opacity: 1
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
          id: river
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
          id: title1
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
---
schema: "1.0"
settings:
  width: 512
  height: 512
  background_color: "#fff"
layers:
  background:
    settings:
      opacity: 1
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
          id: river
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
          id: title1
          offset:
            x: 0
            y: 30
        values:
          text: My subtitle :)
          font_size: 24
          color: "#FFFFFF"
```
TODO: Output Image

### Format

```yaml
schema: "1.0" # see Github for schematic updates

settings: # Canvas settings
  width: # Canvas width, default 1080
  height: # Canvas height, default 1350
  background_color: # Background color

anchors: # Optional anchors for relative positioning (explained later)

layers:
  MY_LAYER_NAME:
    settings: # Layer-related & blend settings, currently only opacity
      opacity: # 0.0 to 1.0
    elements:
      MY_ELEMENT_ID:
        type: # image | text | etc.
        position: # or rel_position, atleast one is mandatory
          ...
        values:
          ...
        operations: # optional
          ...
```


### YAML Variable Substitution

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

Almost every key: constant mapping supports variable substitution, from colors to all numbers. If you notice something missing, please open an issue about it (see README|Contributing and Issues for more info).


### Relative Positioning

Relative positioning is done at a high-level, i.e. during the loading time, keeping the code simple but the template logic more advanced. Either `position` or `rel_position` are *required* for all element types. The offset key is optional and defaults to (0, 0).

Rel. positions can be done relative to anchors which are defined in their own element like so:
```yaml
anchors:
  river:
    x: 350
    y: 275

# (20, 30) from river
rel_position:
  source: anchor
  id: top_left
  offset:
    x: 20
    y: 30
```

Or to another element -- which must have been defined *before* this element.

```yaml
# Relative to another element
rel_position:
  source: element
  id: my_element_identifier
  offset:
    x: 0
    y: 10
```

Lastly, relative positions can also be done in alignment to the canvas. The format for the ID must be in `x-alignment`,`y-alignment`.

x-alignment: left, center, right
y-alignment: top, middle, bottom

```yaml
# Relative to another element
rel_position:
  source: alignment
  id: left,middle
  offset:
    x: -10
    y: 5
```

### Element Reference


### Element Operations
