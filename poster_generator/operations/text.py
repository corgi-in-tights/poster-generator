import random


def randomize_text_color(element) -> None:
    """Randomizes the color of a TextElement object.

    Args:
        element: The TextElement object whose color will be randomized.
    """

    def r():
        return random.randint(0, 255)  # noqa: S311

    element.color = f"#{r():02x}{r():02x}{r():02x}"
