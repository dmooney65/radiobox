import os
import subprocess
from time import sleep
from RPi import GPIO

import psutil
from luma.core.render import canvas
#from luma.core.virtual import viewport
from PIL import ImageFont

import controls
#import dab_ensembles
import dab_options
import fm_menu
import fonts
import menu
import top_menu

from alsa import Pipe
from display import Oled
from MPD2_Client import Client

GPIO_ANTENNA = 13
device = Oled().get_device()
client = Client()
pipe = Pipe()

items = [(fonts.menu_up, 'Back'), (fonts.radio, 'DAB Radio'), (fonts.radio_fm,
                                      'FM Radio')]
 
def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def menu_operation(index):
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup(GPIO_ANTENNA)
    GPIO.setup(GPIO_ANTENNA, GPIO.OUT)
    font = ImageFont.truetype(fonts.font_default, size=12)
    #font_sm = ImageFont.truetype(fonts.font_default, size=10)
    #icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)
    if index == 1:
        GPIO.output(GPIO_ANTENNA, 1)
        client.pause()
        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((5, 10), "DAB: Starting...", font=font, fill="white")
        os.system('../dabpi/dabpi_ctl -x')#, shell=True)
        sleep(.5)
        os.system('../dabpi/dabpi_ctl -a')#, shell=True)
        #sleep(1)
        pipe.start()
        sleep(0.1)
        dab_options.init(1)

    elif index == 2:
        GPIO.output(GPIO_ANTENNA, 1)
        client.pause()
        with canvas(device) as draw:
            draw.text((5, 10), "FM: Starting...", font=font, fill="white")
        os.system('../dabpi/dabpi_ctl -x')
        sleep(.5)
        os.system('../dabpi/dabpi_ctl -b')
        pipe.start()
        #sleep(0.1)
        fm_menu.init(1)

    elif index == 0:
        GPIO.output(GPIO_ANTENNA, 0)
        pipe.stop()
        os.system('../dabpi/dabpi_ctl -x')
        GPIO.cleanup(GPIO_ANTENNA)
        top_menu.init(1)

def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))

def cb_switch(val):
    menu_operation(val % len(items))

def init(val):
    GPIO.setwarnings(False)
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__name__, val)
    
