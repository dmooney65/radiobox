import os
import textwrap
from luma.core.render import canvas
from PIL import ImageFont
import fonts
import menu
import top_menu
from MPD2_Client import Client
import controls
import bt_player
from display import Oled
device = Oled().get_device()
client = Client()

items = [(fonts.menu_up, 'Back'), (fonts.bluetooth_audio, 'Audio'), (fonts.bluetooth, 'Make Discoverable')]

def bt_discover():
    out = os.popen("bluetoothctl discoverable on").readline()
    return out  # (temp.replace("temp=","").replace("'C", "").replace("\n",""))


def menu_operation(index):
    font = ImageFont.truetype(fonts.font_default, size=12)
    #icon = ImageFont.truetype(fonts.font_icon, size=18)
    string = None
    if index == 1:
        client.pause()
        bt_player.init(1)
    elif index == 2:
        height_wrap = fonts.getHeightAndWrap(font)
        height = height_wrap[0]
        wrapper = textwrap.TextWrapper(height_wrap[1])
        string = wrapper.wrap(bt_discover())
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            for i, line in enumerate(string):
                draw.text((2, 0 + (i * height)), text=line,
                          font=font, fill="white")
        
        #radio_menu.init(0)
    elif index == 0:
        top_menu.init(2)
    


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__name__, val)
