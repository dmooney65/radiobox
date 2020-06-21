# -*- encoding: utf-8 -*-
from luma.core.render import canvas
#from luma.core.virtual import viewport
#from PIL import ImageFont, ImageDraw
#import textwrap
import fonts
import top_menu
#import main
import menu
import playing_menu
import controls
from MPD2_Client import Client
from classes import Oled

device = Oled().get_device()
client = Client()

items = [(fonts.playlist_plus, 'Random playlist'),
         (fonts.playlist_play, 'Playlist'), (fonts.menu_up, 'Back')]


def menu_operation(index):
    #font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
    #font_sm = ImageFont.truetype(fonts.font_default, size=10)
    #icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)
    #string = None
    if index == 0:
        client.random()
        playing_menu.init(3)
    elif index == 1:
        playing_menu.init(3)
    elif index == 2:
        top_menu.init(0)


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__import__(__name__), val)
