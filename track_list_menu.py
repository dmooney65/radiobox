from luma.core.render import canvas
import fonts
import menu
import controls
from MPD2_Client import Client
from display import Oled

device = Oled().get_device()
client = Client()
t_list = None
parent = None
parent_index = None
items = []


def menu_operation(index):
    if index == 0:
        global parent
        parent.open(parent_index)
        parent = None
    else:
        global items
        track = t_list[(index -1) % len(t_list)]
        if items[index][0] == fonts.plus:
            song_id = client.add_id(track.get('file'))
            client.prio_id(song_id)
            items[index] = (fonts.minus, items[index][1], items[index][2])
        else:
            p_list = client.playlistinfo()
            for t in p_list:
                if track.get('file') == t.get('file'):
                    client.deleteid(t.get('id'))
                    items[index] = (fonts.plus, items[index][1], items[index][2])
                    break
        draw_menu(index)

def draw_menu(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size = 11, icon_size = 12, icons = False)

def cb_rotate(val):
    draw_menu(val)

def cb_switch(val):
    menu_operation(val % len(items))

def init(val, p, tracks):
    global items
    global t_list
    global parent
    global parent_index
    parent = __import__(p)
    parent_index = val
    t_list = []
    items = []
    items.append((fonts.menu_up, 'Back'))
    p_list = client.playlistinfo()
    for f_name in tracks:
        track = client.find('file', f_name.get('file'))[0]
        ico = fonts.plus
        for song in p_list:
            if track.get('file') == song.get('file'):
                ico = fonts.minus
                break
        t_list.append(track)
        if 'title' in track:
            title = track.get('title')
        else:
            title = 'Empty'
        items.append((ico, title, track.get('artist')))
    draw_menu(0)
    controls.init(__name__, 0)