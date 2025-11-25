from poster_generator import Canvas, TextElement, CircleElement

width = 1080
height = 1350

canvas = Canvas(width=width, height=height, background="#c75d5d")


bg = CircleElement(
    (width//2, height//2),
    radius=(width-128)//2,
    background="#7C2F0B",
)
canvas.add_element("bg", bg)


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