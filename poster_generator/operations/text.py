import random


def randomize_text_color(element) -> dict:
    """Randomizes the color of a TextElement object."""

    def r():
        return random.randint(0, 255)  # noqa: S311

    element.color = f"#{r():02x}{r():02x}{r():02x}"

