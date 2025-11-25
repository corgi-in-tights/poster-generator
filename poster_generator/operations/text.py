import random


def randomize_text_color(text_el: dict) -> dict:
    """Randomizes the color of a TextElement object."""
    def r():
        return random.randint(0, 255)
    
    random_color = f'#{r():02x}{r():02x}{r():02x}'
    text_el["color"] = random_color
    
    return text_el