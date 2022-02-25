from luma.core.render import canvas
import fonts
import menu
import controls
import playing_menu
#import build_indexlist

from MPD2_Client import Client
from display import Oled

device = Oled().get_device()
client = Client()
playlists = None
items = None
parent = None
parent_index = None

def menu_operation(index):
    if index == 0:
        parent.init(parent_index)
    
    else:
        playlist = playlists[(index -1) % len(playlists)]
        client.clear()
        client.load_playlist(playlist.get("playlist"))
        client.playPause()
        playing_menu.init(3)

def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size=11, icon_size=12)


def cb_switch(val):
    menu_operation(val % len(items))

def open(val):
    cb_rotate(val)
    controls.init(__name__, val)

def init(val,p, p_list):
    global items
    global playlists
    global parent
    global parent_index
    items = []
    playlists = []
    parent = __import__(p)
    parent_index = val
    items.append((fonts.menu_up, 'Back'))
    
    for playlist in p_list:
        print(playlist)
        #name = artist.get('artist','empty')
        playlists.append(playlist)
        items.append((fonts.playlist_play, playlist.get("playlist")))
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, 0, font_size=11, icon_size=12)
    controls.init(__name__, 0)
