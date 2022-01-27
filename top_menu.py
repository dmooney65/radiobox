import os
from luma.core.render import canvas
import fonts
import menu
import system_menu
import music_menu
import radio_menu
import bt_menu
import controls
from display import Oled
device = Oled().get_device()

items = [(fonts.music, 'Music'), (fonts.radio, 'Radio'),
         (fonts.bluetooth, 'Bluetooth'), (fonts.hammer_wrench, 'System')]

def bt_discover():
    out = os.popen("bluetoothctl discoverable on").readline()
    return out


def menu_operation(index):
    if index == 0:
        music_menu.init(1)
    elif index == 1:
        radio_menu.init(0)
    elif index == 2:
        bt_menu.init(0)
    elif index == 3:
        system_menu.init(0)


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    device.show()
    #with canvas(device) as draw:
    #    menu.draw_menu(device, draw, items, val)
    cb_rotate(val)
    #device.show()
    controls.init(__name__, val)
    
