import os
import re
from luma.core.render import canvas
import fonts
import menu
import controls
import music_menu
#import build_indexlist
from MPD2_Client import Client
from display import Oled

device = Oled().get_device()
client = Client()
items = None
parent = None
parent_index = None
parent_dir = None
dirs = None

def menu_operation(index):
    if index == 0:
        if len(dirs) > 1:
            dirs.pop(len(dirs)-1)
            parent.init(parent_index, __name__, dirs, True)
        else:
            music_menu.init(parent_index)
    else:
        if items[index][0] == fonts.folder_music:
            dirs.append(items[index][1])
            init(index, __name__, dirs)
        elif items[index][0] == fonts.file_music:
            path = os.path.join(*dirs)
            #print(path)
            #print(items[index][1])
            client.add_id(os.path.join(path,items[index][1]))
            item = (fonts.minus, items[index][1], items[index][2])
            items[index] = item


def redraw(index, sub_dir):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, 0, font_size=11, icon_size=12)
    controls.init(__name__, 0)

def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size=11, icon_size=12)

def cb_switch(val):
    menu_operation(val % len(items))

def cb_long_press(val):
    menu_operation(0)
    
def open(val):
    cb_rotate(val)
    controls.init(__name__, val)

def init(val,p, dir_l, up = False):
    global items
    global parent
    global parent_index
    global parent_dir
    global dirs
    items = []
    index = 0
    if p == __name__ and up:
        index = val
    parent = __import__(p)
    parent_index = val
    dirs = dir_l
    curr_dir = os.path.join(*dirs)
    
    f_list = client.listfiles(curr_dir)
    music_files = re.compile(r'\.(flac|wav|wv|mp3|ape|dsf|dff)')
    for f in f_list:
        if 'directory' in f:
            items.append((fonts.folder_music, f.get('directory'), curr_dir))
        elif 'file' in f:
            if music_files.search(f.get('file')):
                items.append((fonts.file_music, f.get('file'), curr_dir))
        #files.append(f[1])
    items.sort(key=lambda x: x[1], reverse=False)
    items.insert(0,(fonts.menu_up, 'Back'))
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, index, font_size=11, icon_size=12)
    controls.init(__name__, index)
