# from PIL import Image, ImageDraw, ImageFont
# width = 512
# height = 512
# message = "Hello boss!"
# font = ImageFont.truetype("Times", size=20)
#
# img = Image.new('RGB', (width, height), color='blue')
#
# imgDraw = ImageDraw.Draw(img)
#
# textWidth, textHeight = imgDraw.textsize(message, font=font)
# xText = (width - textWidth) / 2
# yText = (height - textHeight) / 2
#
# imgDraw.text((xText, yText), message, font=font, fill=(255, 255, 0))
# img.show()


from pynput import keyboard
from pynput.keyboard import Key


# def keyboard_input():
#     def on_key_release(key):
#         if key == Key.right:
#             print("Right key clicked")
#             return "UMMMMM"
#         elif key == Key.left:
#             print("Left key clicked")
#         elif key == Key.up:
#             print("Up key clicked")
#         elif key == Key.down:
#             print("Down key clicked")
#         elif key == Key.esc:
#             exit()
#
#     with keyboard.Listener(on_release=on_key_release) as listener:
#         listener.join()










