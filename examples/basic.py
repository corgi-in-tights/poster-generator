from poster_generator import Canvas, TextElement

width = 1080
height = 1350

canvas = Canvas(width=width, height=height, background="#c75d5d")

text_element = TextElement(
    (50, 50),
    text="Hello, Poster!",
    font_size=64,
    color="#333333",
)
canvas.add_element("title", text_element)

image = canvas.render()
image.show()

image.save("basic_poster.png")