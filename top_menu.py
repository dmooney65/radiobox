# -*- encoding: utf-8 -*-
import os
import textwrap
from luma.core.render import canvas
from PIL import ImageFont
import fonts
import menu
import system_menu
import music_menu
import radio_menu
import bt_menu
from MPD2_Client import Client
import controls
from classes import Oled
device = Oled().get_device()
client = Client()

items = [(fonts.music, 'Music'), (fonts.radio, 'Radio'),
         (fonts.bluetooth, 'Bluetooth'), (fonts.hammer_wrench, 'System')]

def bt_discover():
    out = os.popen("bluetoothctl discoverable on").readline()
    return out  # (temp.replace("temp=","").replace("'C", "").replace("\n",""))


def menu_operation(index):
    font = ImageFont.truetype(fonts.font_default, size=12)
    #icon = ImageFont.truetype(fonts.font_icon, size=18)
    string = None
    if index == 0:
        music_menu.init(0)
    elif index == 1:
        client.stop()
        radio_menu.init(0)
    elif index == 2:
        bt_menu.init(0)
        #height_wrap = fonts.getHeightAndWrap(font)
        #height = height_wrap[0]
        #wrapper = textwrap.TextWrapper(height_wrap[1])
        #string = wrapper.wrap(bt_discover())
        #with canvas(device) as draw:
        #    draw.rectangle(device.bounding_box, outline="white", fill="black")
        #    for i, line in enumerate(string):
        #        draw.text((2, 0 + (i * height)), text=line,
        #                  font=font, fill="white")
    elif index == 3:
        system_menu.init(0)
    else:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((0, 26), items[index][1], font=font, fill="white")


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__import__(__name__), val)
