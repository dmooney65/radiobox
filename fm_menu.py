#import signal
#import sys
#import textwrap
from time import sleep

from luma.core.render import canvas
from PIL import ImageFont

#import encoding
import controls
import fonts
import menu
import radio_menu
from display import Oled
from radio import FM

device = Oled().get_device()
fm = None
VALUE = 0

items = [fonts.menu_up, fonts.skip_next, fonts.skip_previous]
font = ImageFont.truetype(fonts.font_default, size=12)
font_sm = ImageFont.truetype(fonts.font_default, size=10)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)


def menu_up():
    global fm
    fm.remove_listeners()
    fm = None
    radio_menu.init(2)


def menu_operation(index):
    if index == 0:
        menu_up()
    elif index == 1:
        fm.seek_up()
    elif index == 2:
        fm.seek_down()


def now_playing(draw):
    #draw.text((5, 0), "FM Radio ", font=font_sm, fill="white")
    if fm:
        if fm.rsq_status:
            if fm.rsq_status.frequency > 0:
                draw.text((5, 10), "FM: {} MHz".format(
                    fm.rsq_status.frequency / 100), font=font, fill="white")
                if fm.rds is not None:
                    if fm.rds.name is not None:
                        draw.text((5, 20), fm.rds.name, font=font, fill="white")
        #print("SNR        : {} dB".format(data[11]))
        #print("RSSI       : {} dBuV".format(data[10]))
        #print("Frequency  : {} kHz".format((data[8] << 8 | data[7]) * 10))
        #print("FREQOFF    : ", fm.rsq_status.freq_offset)
        #print("READANTCAP : {}".format(data[13] + (data[14] << 8)))
        else:
            draw.text((5, 10), "FM: Tuning...", font=font, fill="white")


def cb_rotate(val):
    global VALUE
    VALUE = val
    with canvas(device) as draw:
        menu.draw_menu_horizontal(device, draw, items, val % len(items))
        now_playing(draw)


def cb_switch(val):
    global VALUE
    VALUE = val
    menu_operation(val % len(items))


def cb_bt_prev(val):
    fm.seek_down()


def cb_bt_next(val):
    fm.seek_up()


def cb_fm_event(event):
    #global fm
    if fm is not None:
        if fm.rsq_status:
            with canvas(device) as draw:
                menu.draw_menu_horizontal(device, draw, items, VALUE % len(items))
                now_playing(draw)


def init(val):
    global fm
    fm = FM()
    global VALUE
    VALUE = val
    fm.add_listener(cb_fm_event)
    sleep(.5)
    fm.tune_freq(9320)
    with canvas(device) as draw:
        menu.draw_menu_horizontal(device, draw, items, val)
        now_playing(draw)
    controls.init(__name__, val)
