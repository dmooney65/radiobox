import textwrap

#import threading
from luma.core.render import canvas
#from luma.core.virtual import viewport
from PIL import ImageFont

import controls
import fonts
import menu
#import main
import music_menu
from classes import Oled
from MPD2_Client import Client
from timer import InfiniteTimer

#import sys, signal


device = Oled().get_device()

client = Client()
playing = None
timer = None
value = 0
items = [fonts.menu_up, fonts.play_pause, fonts.stop, fonts.skip_next, fonts.skip_previous, fonts.menu]

font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
font_sm = ImageFont.truetype(fonts.font_default, size=10)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)

def tick():
    global playing
    playing = client.poll()
    cb_rotate(value)

def cb_signal_handler(sig, frame):
    if timer:
        print("\ntimer exiting gracefully")
        timer.cancel()

#signal.signal(signal.SIGINT, signal_handler)
def menu_up():
    timer.cancel()
    music_menu.init(1)

def menu_operation(index):
    #if(not client):
    #    client = mpd.connect()
    if index == 0:
        menu_up()
    elif index == 1:
        client.playPause()
    elif index == 2:
        client.stop()
    elif index == 3:
        client.next()
    elif index == 4:
        client.previous()

def now_playing(draw):
    if playing:
        height, wrap = fonts.getHeightAndWrap(font_sm)
        wrapper = textwrap.TextWrapper(wrap)
        song = wrapper.wrap(format(playing.get('title')))
        draw.text((2, 2), "Now Playing: ", font=font_sm, fill="white")
        artist = playing.get('artist')
        if artist:
            if isinstance(artist, list):
                draw.text((2, height + 2), artist[0] + " ", font=font_sm, fill="white")
            else:
                draw.text((2, height + 2), artist + " ", font=font_sm, fill="white")
        for i, line in enumerate(song):
            draw.text((2, (height*2 + 2) + (i * height)), text=line + " ", font=font_sm, fill="white")
    else:
        draw.text((5, 0), "Stopped", fill="white")

def cb_rotate(val):
    global value
    value = val
    with canvas(device) as draw:
        menu.draw_menu_horizontal(device, draw, items, value % len(items))
        now_playing(draw)

def cb_switch(val):
    global value
    value = val
    menu_operation(value % len(items))

def cb_bt_next(val):
    client.next()

def cb_bt_prev(val):
    client.previous()

def cb_bt_play_pause(val):
    client.playPause()

def cb_bt_mute(val):
    menu_up()

def init(val):
    global value
    global playing
    global timer
    value = val
    playing = client.poll()
    # Example Usage
    timer = InfiniteTimer(1, tick)
    timer.start()
    with canvas(device) as draw:
        menu.draw_menu_horizontal(device, draw, items, value)
        now_playing(draw)
    controls.init(__import__(__name__), val)
