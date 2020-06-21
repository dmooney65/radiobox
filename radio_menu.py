import os
#import sys
import signal
import subprocess
import time

import psutil
from luma.core.render import canvas
#from luma.core.virtual import viewport
from PIL import ImageFont

#import threading
import controls
import fonts
import menu
import top_menu
#import alsaaudio as audio
#import asyncio
#from threading import Thread
from classes import Oled
from alsa import Pipe

#import textwrap


device = Oled().get_device()
pipe = Pipe()

items = [(fonts.radio, 'DAB Radio'), (fonts.radio_fm,
                                      'FM Radio'), (fonts.menu_up, 'Back')]


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def menu_operation(index):
    
    font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
    #font_sm = ImageFont.truetype(fonts.font_default, size=10)
    #icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)
    if index == 0:
        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 20), "DAB Tuning...", font=font, fill="white")
        playing = True
        pipe.start()
        os.system('../dabpi/dabpi_ctl -a')
        os.system('../dabpi/dabpi_ctl -j 17')
        os.system('../dabpi/dabpi_ctl -i 9')
        time.sleep(1)
        #subprocess.run(['../dabpi/dabpi_ctl', '-g'])
        os.system('../dabpi/dabpi_ctl -f 7')

    elif index == 1:
        with canvas(device) as draw:
            draw.text((2, 20), "FM Selected", font=font, fill="white")
    elif index == 2:
        pipe.stop()
        os.system('../dabpi/dabpi_ctl -x')
        top_menu.init(1)


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    #global client
    #client = Client()
    #print("in main")
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__import__(__name__), val)
