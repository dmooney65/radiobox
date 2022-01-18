
from luma.core.render import canvas
from PIL import ImageFont
import menu
import fonts
import system_menu
import controls
from display import Oled

device = Oled().get_device()
#canvas = None
#value = 0
adj_list = (0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176,
            192, 208, 224, 240, 255)  # Contrast value range


def cb_rotate(val):
    device.contrast(adj_list[val % len(adj_list)])

def cb_switch(val):
    system_menu.init(6)

def init(val):
    #print("in contrast")
    font = ImageFont.truetype(fonts.font_default, size=12)
    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white", fill="black")
        menu.draw_text(draw, 0, 26, "Contrast", font=font)
    controls.init(__name__, val)
