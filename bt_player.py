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
import textwrap
from luma.core.render import canvas
from PIL import ImageFont

import bt_menu
import controls
import fonts
import menu
from bluezero import dbus_tools, media_player
from classes import Oled

value = 0
# Find the mac address of the first media player connected over Bluetooth
#MAC_ADDR = None
device = Oled().get_device()

items = [fonts.menu_up, fonts.play_pause, fonts.stop, fonts.fast_forward, fonts.rewind]
font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
font_sm = ImageFont.truetype(fonts.font_default, size=10)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)

def menu_up():
    #timer.cancel()
    bt_menu.init(0)

def menu_operation(index):
    #if(not client):
    #    client = mpd.connect()
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

def find_player():
    for dbus_path in dbus_tools.get_managed_objects():
        #print(dbus_path)
        if 'player' in dbus_path:   
            mac_addr = dbus_tools.get_mac_addr_from_dbus_path(dbus_path)
            return mac_addr

def pause():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        media_status = mp.status
        print(media_status)
        if media_status == 'playing':
            mp.pause()


def play_pause():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        media_status = mp.status
        print(media_status)
        if media_status == 'playing':
            mp.pause()
        else:
            mp.play()

def fast_forward():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        mp.fast_forward()
        #sleep(2)
        mp.play()

def rewind():
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        mp.rewind()
        #sleep(2)
        mp.play()

def now_playing(draw):
    mac_addr = find_player()
    if mac_addr:
        mp = media_player.MediaPlayer(mac_addr)
        playing = mp.track
        #for detail in playing:
        #    print(f'{detail} : {playing[detail]}')
        height, wrap = fonts.getHeightAndWrap(font_sm)
        wrapper = textwrap.TextWrapper(wrap)
        song = wrapper.wrap(format(playing.get('Title')))
        #album = wrapper.wrap(format(playing.get('Album')))
        draw.text((2, 2), mp.name + ": ", font=font_sm, fill="white")
        artist = playing.get('Artist')
        if artist:
            if isinstance(artist, list):
                draw.text((2, height + 2), artist[0] + " ", font=font_sm, fill="white")
            else:
                draw.text((2, height + 2), artist + " ", font=font_sm, fill="white")
        #for i, line in enumerate(album):
        #    draw.text((2, (height*2 + 2) + (i * height)), text=line + " ", font=font_sm, fill="white")
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

def cb_bt_play_pause(val):
    play_pause()

def cb_bt_prev(val):
    rewind()

def cb_bt_next(val):
    fast_forward()

def init(val):
    global value
    #global playing
    #global timer
    value = val
    #playing = client.poll()
    # Example Usage
    #timer = InfiniteTimer(1, tick)
    #timer.start()
    with canvas(device) as draw:
        menu.draw_menu_horizontal(device, draw, items, value)
        now_playing(draw)
    controls.init(__import__(__name__), val)
