#from luma.core.render import canvas
from PIL import ImageFont
from math import floor
import fonts


def draw_text(draw, pos_x, pos_y, text, font=fonts.font_default, invert=False, height=10, width=20):
    #draw.rectangle(device.bounding_box, outline="white", fill="black")
    if text:
        if invert:
            draw.rectangle((pos_x, pos_y+1, pos_x+width, pos_y +
                            height), outline="white", fill="white")
            draw.text((pos_x, pos_y), text, font=font,
                    outline="white", fill="black")
        else:
            draw.text((pos_x, pos_y), text, font=font,
                    outline="black", fill="white")


def draw_menu(device, draw, menustr, index, font_size=14, icon_size=17, icons=True):
    font = ImageFont.truetype(fonts.font_default, font_size)
    icon = ImageFont.truetype(fonts.font_icon, icon_size)
    #icon = ImageFont.truetype(fonts.font_default, icon_size)
    width, height = icon.getsize(fonts.radio)
    # number of lines before scrolling needed
    scroll_lines = floor(device.height // height)
    offset = 0
    max_scroll = len(menustr) - scroll_lines
    if index >= scroll_lines:  # Scroll menu
        offset = index - (index % scroll_lines)
        if offset >= max_scroll:
            offset = max_scroll
    for idx, val in enumerate(menustr[offset:offset + scroll_lines], start = offset):
        ico = val[0]
        text = val[1]
        text_sz = font.getsize(text)
        if idx == index:
            draw_text(draw, 2, (idx - offset) * height, ico, font=icon,
                      invert=True, height=height, width=width + 1)
            draw_text(draw, 2 + width + 2, (idx - offset) * height, text,
                      font=font, invert=True, height=height, width=text_sz[0] + 1)
        else:
            draw_text(draw, 2, (idx - offset) * height, ico, font=icon)
            draw_text(draw, 2 + width + 2, (idx - offset)
                      * height, text, font=font)

def draw_menu_horizontal(device, draw, menustr, index=0, icon_size=18):
    
    icon = ImageFont.truetype(fonts.font_icon, size=icon_size)

    width, height = icon.getsize(menustr[0])

    for idx, val in enumerate(menustr):
        if idx == index:
            draw_text(draw, idx * width, device.height - height,
                      val, font=icon, invert=True, height=height, width=width)
        else:
            draw_text(draw, idx * width, device.height -
                      height, val, font=icon)
