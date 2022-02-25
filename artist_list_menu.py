from luma.core.render import canvas
import fonts
import menu
import controls
import album_list_menu
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
        parent.open(parent_index)
    else:
        artist = artists[(index -1) % len(artists)]
        albs = client.get_list('album', 'artist', artist)
        albums = []
        for alb in albs:
            albums.append(alb.get('album'))
        album_list_menu.init(index, __name__, albums, artist)


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size=11, icon_size=12)


def cb_switch(val):
    menu_operation(val % len(items))
    
def open(val):
    cb_rotate(val)
    controls.init(__name__, val)

def init(val,p, a):
    global items
    global artists
    global parent
    global parent_index
    items = []
    artists = []
    parent = __import__(p)
    parent_index = val
    items.append((fonts.menu_up, 'Back'))
    #artists = client.get_list('artist')
    for artist in a:
        #print(artist)
        #name = artist.get('artist','empty')
        artists.append(artist)
        items.append((fonts.account_artist, artist))
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, 0, font_size=11, icon_size=12)
    controls.init(__name__, 0)
