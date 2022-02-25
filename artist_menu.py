from luma.core.render import canvas
import fonts
import menu
import controls
import artist_list_menu
import build_indexlist
from MPD2_Client import Client
from display import Oled

device = Oled().get_device()
client = Client()
artists = None
items = None
parent = None
parent_index = None

def menu_operation(index):
    if index == 0:
        parent.init(parent_index)
    else:
        artist_list_menu.init(index, __name__, artists[index - 1])


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size=11, icon_size=12)


def cb_switch(val):
    menu_operation(val % len(items))

def open(val):
    cb_rotate(val)
    controls.init(__name__, val)

def init(val,p, arts):
    global items
    global artists
    global parent
    global parent_index
    items = []
    artists = []
    parent = __import__(p)
    parent_index = val
    items.append((fonts.menu_up, 'Back'))
    index_list = build_indexlist.get_list(arts, 'artist')
    for l in index_list:
        items.append((fonts.account_artist, l[0]))
        artists.append(l[1])
    
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, 0, font_size=11, icon_size=12)
    controls.init(__name__, 0)
