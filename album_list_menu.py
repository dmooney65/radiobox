from luma.core.render import canvas
import fonts
import menu
import controls
import track_list_menu
from MPD2_Client import Client
from display import Oled

device = Oled().get_device()
client = Client()
albums = None
parent = None
parent_index = None

items = None

def open(val):
    cb_rotate(val)
    controls.init(__name__, val)

def menu_operation(index):
    if index == 0:
        parent.open(parent_index)
    else:
        album = albums[(index -1) % len(albums)]
        artist = items[index][2]
        if album == ' ':
            album = ''
        if artist:
            tracks = client.get_list('file', 'album', album, 'artist', artist)
        else:
            tracks = client.get_list('file', 'album', album)
        track_list_menu.init(index, __name__, tracks)


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size=11, icon_size=12)


def cb_switch(val):
    menu_operation(val % len(items))

def init(val, p, albs, artist = None):
    global items
    global albums
    global parent
    global parent_index
    parent_index = val
    parent = __import__(p)
    items = []
    items.append((fonts.menu_up, 'Back'))
    albums = []
    for album in albs:
        albums.append(album)
        #if album.album:
        print(album)
        items.append((fonts.album, album, artist))
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, 0, font_size=11, icon_size=12)
    controls.init(__name__, 0)
