from poster_generator import Canvas, TextElement, RectangleElement

width = 1080
height = 1080

canvas = Canvas(width=width, height=height, background="#5e4444")


bg = RectangleElement(
    width=(width-128)//2,
    height=(height-128)//2,
    fill="#59473F",
    outline="#3F2E2E",
    outline_width=8,
)
canvas.add_element("bg", bg)
bg.align_to(x_align=0.5, y_align=0.5)


text_element = TextElement(
    text="Hello, Poster!",
    font_size=64,
    fill="#FFFFFF",
)
canvas.add_element("title", text_element)
text_element.align_to(x_align=0.5, y_align=0.5)
print(text_element.get_size(), text_element.position)


image = canvas.render()
image.show()
