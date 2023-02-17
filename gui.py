import tkinter as tk
from PIL import Image, ImageDraw, ImageFont


window = tk.Tk()
window.geometry("400x400")


tile_colours = {
            2048: "EDC22E",     # 237, 194, 46
            1024: "#EDC23F",
            512: "#EDC850",
            256: "#EDCC61",
            128: "#EDCF72",
            64: "#F65E3B",  # 246, 94, 59
            32: "#F67C5F",
            16: "#F59563",
            8: "#F2B179",
            4: "#EDE0C8",
            2: "#EEE4DA",
            0: "#CCC0B3"
        }


def assemble_image(number, dimensions):
    tile_colours_rgb = {
        2048: (237, 194, 46),
        1024: "#EDC23F",
        512: "#EDC850",
        256: "#EDCC61",
        128: "#EDCF72",
        64: (246, 94, 59),
        32: "#F67C5F",
        16: "#F59563",
        8: "#F2B179",
        4: "#EDE0C8",
        2: "#EEE4DA",
        0: "#CCC0B3"
    }
    width, height = dimensions
    img = Image.new('RGB', dimensions, tile_colours_rgb[number])
    imgDraw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Times", size=20)

    (imgDraw.textsize(number, font=font))
    #textWidth, textHeight = imgDraw.textsize(number, font=font)
    #xText = (width - textWidth) / 2
    #yText = (height - textHeight) / 2

    #imgDraw.text((xText, yText), "message", fill=(255, 255, 255), font=font)
    img.show()


'''img = Image.new('RGB', (300, 200), (237, 194, 46))
imgDraw = ImageDraw.Draw(img)
font = ImageFont.truetype("Times", size=80)
imgDraw.text((10, 10), "message", fill=(255, 255, 255), font=font)
img.show()'''

box = tk.Label(window, text="ok")
box.grid(row=0, column=0)


def assemble_text_grid(board_list):
    pass


def launch_window():
    tk.mainloop()





