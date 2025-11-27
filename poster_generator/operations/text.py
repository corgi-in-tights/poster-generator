import random


def randomize_text_color(text_element, *args, **kwargs) -> dict:
    """Randomizes the color of a TextElement object."""

    def r():
        return random.randint(0, 255)  # noqa: S311

    text_element.color = f"#{r():02x}{r():02x}{r():02x}"

