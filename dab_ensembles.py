from time import sleep
from luma.core.render import canvas
from PIL import ImageFont

#import encoding
import controls
import fonts
import menu
import radio_menu
from display import Oled
from radio import DAB
import dab_menu
from dab_db import DABDatabase

device = Oled().get_device()
#dab = None
#VALUE = 0
db = DABDatabase()


font = ImageFont.truetype(fonts.font_default, size=12)
font_sm = ImageFont.truetype(fonts.font_default, size=10)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)


class State:
    value = 0
    dab = None
    items = []

    def __init__(self, value=0, dab=None):
        self.value = value
        self.dab = dab

    def set_value(self, val):
        self.value = val

    def set_dab(self, dab):
        self.dab = dab
    
    def set_items(self, items):
        self.items = items

state = State()

def menu_up():
    #global dab
    state.dab.remove_radio_listener()
    # dab.remove_listener()
    dab = None
    radio_menu.init(1)


def redraw():
    state.dab.add_listener(cb_dab_event)
    draw_menu()
    controls.init(__name__, state.value)


def menu_operation(index):
    #size = len(items)
    if index == 0:
        menu_up()
    else:
        state.dab.remove_listener()
        dab_menu.init(state.items[index][2], state.dab)


def draw_menu():
    with canvas(device) as draw:
        menu.draw_menu(device, draw, state.items, state.value %
                       len(state.items), font_size=12, icon_size=14)


def now_playing(draw):
    draw.text((5, 10), "DAB: Scanning...", font=font, fill="white")


def cb_rotate(val):
    #global VALUE
    #VALUE = val
    state.set_value(val)
    draw_menu()


def cb_switch(val):
    #global VALUE
    #VALUE = val
    state.set_value(val)
    menu_operation(state.value % len(state.items))


def cb_dab_event(event):
    if state.dab is not None:
        #global items
        if event == 'ensembles':
            create_items()
            draw_menu()


def create_items():
    state.dab.add_listener(cb_dab_event)
    rows = db.get_ensembles()
    global items
    items = []
    if len(rows) == 0:
        state.dab.scan()
    else:
        state.items.append((fonts.menu_up, 'Back'))
        for row in rows:
            state.items.append(('', row[0], row[1]))
        # dab.scan()
    draw_menu()


def init(val):
    #global dab
    #dab = DAB()
    state.set_dab(DAB())
    state.set_value(val)
    #global VALUE
    #VALUE = val
    #state
    # dab.add_radio_listener()
    state.dab.add_listener(cb_dab_event)
    sleep(.1)
    # dab.tune_frequency(9)
    with canvas(device) as draw:
        now_playing(draw)
    create_items()
    controls.init(__name__, val)
