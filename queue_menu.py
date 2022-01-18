from luma.core.render import canvas
import fonts
import menu
import controls
import playing_menu
from MPD2_Client import Client
from display import Oled
from timer import InfiniteTimer
from state import State

device = Oled().get_device()
client = Client()
state = State()
queue = None
items = []


def menu_operation(index):
    if index == 0:
        state.timer.cancel()
        playing_menu.init(6)

def delete(index):
    song = queue[(index -1) % len(queue)]
    print(song)

def draw_menu():
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, state.value % len(items), font_size = 11, icon_size = 12)
    device.show()

def cb_rotate(val):
    state.set_value(val)
    draw_menu()


def cb_switch(val):
    state.set_value(val % len(items))
    if state.value == 0:
        menu_operation(0)
    else:
        if items[state.value][0] == fonts.pause or items[state.value][0] == fonts.play:
            client.playPause()
        else:
            song = queue[state.value -1]
            client.seek(song.get('pos'), 0)

def cb_long_press(val):
    menu_operation(0)

def cb_signal_handler(sig, frame):
    if state.timer:
        print("queue timer exiting gracefully")
        state.timer.cancel()
    else:
        print("no queue timer")


def tick():
    global items
    oldsong = state.status.get('song')
    oldstatus = state.status.get('state') 
    state.status = client.status()
    if oldsong != state.status.get('song') or oldstatus != state.status.get('state'):        
        for i, item in enumerate(items):
            if item[0] is not fonts.minus and i > 0:
                new = (fonts.minus, item[1])
                items[i] = new
        if state.status.get('song'): #playlist complete
            idx = int(state.status.get('song'))+1
            song_text = items[idx][1]
            if state.status.get('state') == 'play':
                items[idx] = (fonts.pause, song_text)
            else:
                items[idx] = (fonts.play, song_text)
            state.set_value(idx)
        controls.reset_ts()
        draw_menu()


def init(val):
    global items
    global queue
    state.status = client.status()
    state.set_value(int(state.status.get('song'))+1)
    queue = []
    items = []
    items.append((fonts.menu_up, 'Back'))
    p_list = client.playlistinfo()
    for i, song in enumerate(p_list):
        queue.append(song)
        icon = fonts.minus
        if state.value-1 == i:
            if state.status.get('state') == 'play':
                icon = fonts.pause
            else:
                icon = fonts.play
        title = song.get('title')
        if title == None:
            title = client.title_from_file(song.get('file'))
        items.append((icon, title))
    
    if state.timer:
        state.timer.cancel()
    state.timer = InfiniteTimer(1, tick)
    state.timer.start()
    draw_menu()
    controls.init(__name__, state.value)