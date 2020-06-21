import time
import os
import socket
import textwrap
import psutil

from luma.core.render import canvas
from luma.core.virtual import viewport
from PIL import ImageFont

import fonts
import menu
import controls
import top_menu
import contrast
from classes import Oled

device = Oled().get_device()


def ip_address():
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(("8.8.8.8", 80))
    ip_addr = (sck.getsockname()[0])
    sck.close()
    return str(ip_addr)


def get_ip_addresses(family):
    for interface, nics in psutil.net_if_addrs().items():
        for nic in nics:
            if nic.family == family:
                yield (interface, nic.address)


def gpu_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=", "").replace("'C", "").replace("\n", "")


items = [(fonts.ip, 'IP Address'), (fonts.coolant_temp, 'Temperatures'), (fonts.google_downasaur, 'Shutdown'),
         (fonts.reload_icon, 'Restart'), (fonts.brightness, 'Contrast'), (fonts.raspberry_pi, 'CPU Usage'), (fonts.menu_up, 'Back')]


def menu_operation(index):
    font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
    #font_sm = ImageFont.truetype(fonts.font_default, size=10)
    #icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)
    string = None
    degree_sign = u'\N{DEGREE SIGN}'
    if index == 0:
        with canvas(device) as draw:
            ipv4s = list(get_ip_addresses(socket.AF_INET))
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            #draw.text((2, 26), ip_address(), font=font, fill="white")
            draw.text((2, 26), ipv4s[1][1], font=font, fill="white")
    elif index == 1:
        with canvas(device) as draw:
            temps = psutil.sensors_temperatures()
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 10), "CPU= "+format(temps.get('cpu-thermal')
                                              [0].current)+degree_sign+"C", font=font, fill="white")
            draw.text((2, 26), "GPU= "+gpu_temp() +
                      degree_sign+"C", font=font, fill="white")
    elif index == 2:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 26), "Shutting down...", font=font, fill="white")
            time.sleep(3)
            os.system('sudo shutdown now')
    elif index == 3:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 26), "Restarting...", font=font, fill="white")
            time.sleep(3)
            #os.popen("vcgencmd measure_temp")
            os.system('sudo reboot')
    elif index == 4:
        contrast.init(0)
    elif index == 5:
        height, wrap = fonts.getHeightAndWrap(font)
        wrapper = textwrap.TextWrapper(wrap)
        string = wrapper.wrap(text=format(
            psutil.cpu_times_percent(percpu=False)))
        v_height = (len(string) * height) + 2
        virtual = viewport(device, width=device.width, height=v_height)
        with canvas(virtual) as draw:
            for i, line in enumerate(string):
                draw.text((2, 0 + (i * height)), text=line,
                          font=font, fill="white")
        time.sleep(2)
        for pos_y in range(v_height - (device.height)):
            virtual.set_position((0, pos_y))
            time.sleep(0.01)
    else:
        top_menu.init(3)


def cb_rotate(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items))


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val)
    controls.init(__import__(__name__), val)
