from time import sleep

from luma.core.render import canvas
#from luma.core.virtual import viewport
from PIL import ImageFont

import controls
import dab_ensembles
import fonts
import menu
import radio_menu

from alsa import Pipe
from display import Oled
from MPD2_Client import Client

device = Oled().get_device()

items = [(fonts.menu_up, 'Back'), (fonts.star, 'Favourites'), (fonts.playlist_play,
                                      'All'), (fonts.reload_icon, 'Rescan')]

def menu_operation(index):
    font = ImageFont.truetype(fonts.font_default, size=12)
    #font_sm = ImageFont.truetype(fonts.font_default, size=10)
    #icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)
    if index == 1:
        with canvas(device) as draw:
            draw.text((5, 10), "DAB: Loading Favourites...", font=font, fill="white")
        dab_ensembles.init('favourites', 0)

    elif index == 2:
        with canvas(device) as draw:
            draw.text((5, 10), "DAB: Loading All...", font=font, fill="white")
        dab_ensembles.init('all',0)
    
    elif index == 3:
        with canvas(device) as draw:
            draw.text((5, 10), "DAB: Loading All...", font=font, fill="white")
        dab_ensembles.init('rescan',0)

    elif index == 0:
        radio_menu.init(1)

def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))

def cb_switch(val):
    menu_operation(val % len(items))

def init(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__name__, val)
    