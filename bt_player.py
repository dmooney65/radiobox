#  When using your Linux computer as a Bluetooth speaker the MediaPlayer
#  interfaces allows you interact with the media player on the other end of
#  the Bluetooth connection.
#  e.g. the music player on your phone.
#  This script displays information about the current track.
#  Before you can run this scrip you have to pair and connect your audio
#  source. For simplicity we can do this on the command line with the
#  bluetoothctl tool
#     pi@RPi3:~ $ bluetoothctl
#     [bluetooth]# agent NoInputNoOutput
#     Agent registered
#     [bluetooth]# discoverable on
#     Changing discoverable on succeeded
#     [CHG] Controller B8:27:EB:22:57:E0 Discoverable: yes
#
#  Now we have made the Raspberry Pi discoverable we can pair to it from the
#  mobile phone. Once it has paired you can tell the Raspberry Pi that it is a
#  trusted device
#
#     [Nexus 5X]# trust 64:BC:0C:F6:22:F8
#
#  Now the phone is connected you can run this script to find which track is
#  playing
#
#     pi@RPi3:~ $ python3 examples/control_media_player.py
# Battery command for remote 
# dbus-send --print-reply=literal --system --dest=org.bluez /org/bluez/hci0/dev_FF_FF_80_01_46_7B org.freedesktop.DBus.Properties.Get string:"org.bluez.Battery1" string:"Percentage"
from time import sleep
import textwrap
from luma.core.render import canvas
from PIL import ImageFont
import dbus
import bt_menu
import controls
import fonts
import menu
from bluezero import dbus_tools, media_player
from display import Oled
from timer import InfiniteTimer
from state import State

device = Oled().get_device()
state = State()

items = [fonts.menu_up, fonts.play, fonts.stop, fonts.fast_forward, fonts.rewind]
font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
font_sm = ImageFont.truetype(fonts.font_default, size=11)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)

def menu_up():
    if state.timer:
        state.timer.cancel()
    bt_menu.init(1)

def menu_operation(index):
    if index == 0:
        menu_up()
    elif index == 1:
        play_pause()
    elif index == 2:
        pause()
    elif index == 3:
        fast_forward()
    elif index == 4:
        rewind()

def update_icons():
    if state.playing == 'playing':
        items[1] = fonts.pause
    else:
        items[1] = fonts.play

def find_player():
    for dbus_path in dbus_tools.get_managed_objects():
        if dbus_path.endswith('player0'):
            mac_addr = dbus_tools.get_device_address_from_dbus_path(dbus_path)
            return mac_addr

def pause():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        media_status = mp.status
        if media_status == 'playing':
            mp.pause()
            state.playing = 'paused'


def play_pause():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        media_status = mp.status
        #print(media_status)
        if media_status == 'playing':
            mp.pause()
            state.playing = 'paused'
        else:
            mp.play()
            state.playing = 'playing'        

def fast_forward():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        mp.fast_forward()
        sleep(0.2)
        mp.play()

def rewind():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        mp.rewind()
        sleep(0.2)
        mp.play()

def cb_signal_handler(sig, frame):
    if state.timer:
        print("bt timer exiting gracefully")
        state.timer.cancel()
    else:
        print("no bt timer")


def now_playing(draw):
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        state.playing = mp.status
        playing = {}
        try:
            playing = mp.track
        except dbus.exceptions.DBusException as dummy:
            pass
        height, wrap = fonts.getHeightAndWrap(font_sm)
        wrapper = textwrap.TextWrapper(wrap)
        song = wrapper.wrap(format(playing.get('Title')))
        #draw.text((2, 2), mp.name + ": ", font=font_sm, fill="white")
        artist = playing.get('Artist')
        if artist:
            if isinstance(artist, list):
                draw.text((2, 2), artist[0] + " ", font=font_sm, fill="white")
            else:
                draw.text((2, 2), artist + " ", font=font_sm, fill="white")
        for i, line in enumerate(song):
            draw.text((2, (height + 2) + (i * height)), text=line + " ", font=font_sm, fill="white")
    else:
        draw.text((5, 0), "Stopped", fill="white")

def cb_rotate(val):
    state.set_value(val)
    draw_menu()

def draw_menu():
    update_icons()
    with canvas(device) as draw:
        menu.draw_menu_horizontal(device, draw, items, state.value % len(items))
        now_playing(draw)

def cb_switch(val):
    state.set_value(val)
    menu_operation(state.value % len(items))

def cb_bt_play_pause():
    play_pause()

def cb_bt_prev():
    rewind()

def cb_bt_next():
    fast_forward()

def tick():
    controls.reset_ts()
    draw_menu()

def init(val):
    state.set_value(val)
    with canvas(device) as draw:
        update_icons()
        menu.draw_menu_horizontal(device, draw, items, state.value)
        now_playing(draw)
    
    state.timer = InfiniteTimer(1, tick)
    state.timer.start()
    controls.init(__name__, val)