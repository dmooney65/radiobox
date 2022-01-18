import textwrap

from luma.core.render import canvas
from PIL import ImageFont

import controls
import fonts
import menu
import music_menu
import queue_menu
from display import Oled
from MPD2_Client import Client
from timer import InfiniteTimer
from state import State

device = Oled().get_device()

client = Client()
state = State()

items = [fonts.menu_up, fonts.play, fonts.stop, fonts.skip_next,
         fonts.skip_previous, fonts.shuffle_disabled, fonts.playlist_music, fonts.playlist_remove]

font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
font_sm = ImageFont.truetype(fonts.font_default, size=11)
font_sm_i = ImageFont.truetype(fonts.font_italic, size=11)
font_sm_b = ImageFont.truetype(fonts.font_bold, size=11)

icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)


def tick():
    if not state.pause_timer:
        global items
        oldtitle = state.playing.get('title')
        oldstatus = state.status.get('state')
        oldshuffle = state.status.get('random')
        state.playing = client.poll()
        state.status = client.status()
        if oldtitle != state.playing.get('title') or oldstatus != state.status.get('state') or oldshuffle != state.status.get('random'):
            update_icons()
            controls.reset_ts()
            #cb_rotate(state.value)
            draw_menu()

def update_icons():
    if state.status.get('state') == 'play':
        items[1] = fonts.pause
    else:
        items[1] = fonts.play
    if state.status.get('random') == '1':
        items[5] = fonts.shuffle
    else:
        items[5] = fonts.shuffle_disabled

def cb_signal_handler(sig, frame):
    if state.timer:
        print("playing timer exiting gracefully")
        state.timer.cancel()
    else:
        print("no playing timer")


def menu_up():
    if state.timer:
        print("playing timer exiting gracefully")
        state.timer.cancel()
    music_menu.init(1)


def menu_operation(index):
    if index == 0:
        menu_up()
    elif index == 1:
        client.playPause()
    elif index == 2:
        client.stop()
    elif index == 3:
        nextsong()
    elif index == 4:
        prevsong()
    elif index == 5:
        if state.status.get('random') == '1':
            client.random(0)
        else:
            client.random(1)
    elif index == 6:
        if state.playing:
            state.timer.cancel()
            queue_menu.init(0)


def nextsong():
    if state.playing:
        if state.status.get('nextsong'):
            client.seek(state.status.get('nextsong'), 0)


def prevsong():
    if state.playing:
        song = int(state.status.get('song'))
        if song > 0:
            client.seek((str(song-1)), 0)


def now_playing(draw):
    state.playing = client.poll()
    state.status = client.status()
    if state.playing:
        height, wrap = fonts.getHeightAndWrap(
            font_sm, format(state.playing.get('title')))
        wrapper = textwrap.TextWrapper(wrap)
        song = wrapper.wrap(format(state.playing.get('title')))
        artist = state.playing.get('artist')
        if artist:
            if isinstance(artist, list):
                draw.text((2, 0), '{},{}'.format(*artist),
                          font=font_sm_b, fill="white")
            else:
                draw.text((2, 0), artist + " ", font=font_sm_b, fill="white")
        album = state.playing.get('album')
        if album:
            draw.text((2, height), album + " ", font=font_sm_i, fill="white")
        for i, line in enumerate(song):
            if i < 2:
                draw.text((2, (height*2) + (i * height)),
                          text=line + " ", font=font_sm, fill="white")
    else:
        draw.text((5, 0), "Stopped", fill="white")


def draw_menu():
    with canvas(device) as draw:
        menu.draw_menu_horizontal(
            device, draw, items, state.value % len(items), icon_size=16)
        now_playing(draw)
    device.show()

def cb_rotate(val):
    state.set_pause_timer(True)
    state.set_value(val)
    draw_menu()
    state.set_pause_timer(False)


def cb_switch(val):
    state.set_value(val)
    menu_operation(state.value % len(items))


def cb_long_press(val):
    if state.value % len(items) == 7:
        client.clear()


def cb_bt_next():
    nextsong()


def cb_bt_prev():
    prevsong()


def cb_bt_play_pause():
    client.playPause()


def cb_bt_mute():
    client.playPause()#menu_up()


def init(val):
    state.set_value(val)
    # client.replayGain('off')
    state.playing = client.poll()
    state.status = client.status()
    update_icons()
    if state.timer:
        state.timer.cancel()
    state.timer = InfiniteTimer(.5, tick)
    state.timer.start()
    draw_menu()
    controls.init(__name__, val)
