from poster_generator import Canvas, TextElement, CircleElement

width = 1080
height = 1350

canvas = Canvas(width=width, height=height, background="#c75d5d")


bg = CircleElement(
    (width//2, height//2),
    radius=(width-128)//2,
    background="#7C2F0B",
    outline_color="#FFFFFF",
    outline_width=8,
)
canvas.add_element("bg", bg)


text_element = TextElement(
    (0, 0),
    text="Hello, Poster!",
    font_size=64,
    color="#333333",
)
canvas.add_element("title", text_element)
text_element.align_to(canvas, x_align="center", y_align="center")


image = canvas.render()
image.show()
# image.save("basic_poster.png")
