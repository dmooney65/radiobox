import os
import socket
import textwrap
from time import sleep

import psutil
from luma.core.render import canvas
from luma.core.virtual import viewport
from PIL import ImageFont

import contrast
import controls
import fonts
import menu
import top_menu
from display import Oled

device = Oled().get_device()


def get_ip_addresses(family):
    for interface, nics in psutil.net_if_addrs().items():
        for nic in nics:
            if nic.family == family:
                yield (interface, nic.address)


def gpu_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=", "").replace("'C", "").replace("\n", "")


items = [(fonts.menu_up, 'Back'), (fonts.wifi, 'Toggle Hotspot'), (fonts.ip, 'IP Address'), (fonts.coolant_temp, 'Temperatures'), (fonts.reload_icon, 'Reload'),
         (fonts.google_downasaur, 'Shutdown'), (fonts.brightness, 'Contrast'), (fonts.raspberry_pi, 'CPU Usage'), (fonts.lightning, 'Restore wifi')]


def menu_operation(index):
    font = ImageFont.truetype(fonts.font_default, size=fonts.size_default)
    font_sm = ImageFont.truetype(fonts.font_default, size=11)
    #icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)
    string = None
    degree_sign = u'\N{DEGREE SIGN}'
    if index == 1:
        #os.system('sudo /usr/bin/autohotspot')
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 26), "Doing nothing...", font=font, fill="white")
        sleep(1)
        #os.system('sudo /usr/bin/autohotspot')
    elif index == 2:
        with canvas(device) as draw:
            ipv4s = list(get_ip_addresses(socket.AF_INET))
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 26), ipv4s[1][1], font=font, fill="white")
    elif index == 3:
        with canvas(device) as draw:
            temps = psutil.sensors_temperatures()
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 10), "CPU= "+format(temps.get('cpu_thermal')
                                              [0].current)+degree_sign+"C", font=font, fill="white")
            draw.text((2, 26), "GPU= "+gpu_temp() +
                      degree_sign+"C", font=font, fill="white")
    elif index == 4:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 26), "Reloading...", font=font, fill="white")
        sleep(1)
        os.system('sudo systemctl restart stalk_control.service')
    elif index == 5:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 26), "Shutting down...", font=font, fill="white")
        sleep(1)
        os.system('sudo shutdown now')
    elif index == 6:
        contrast.init(0)
    elif index == 7:
        height, wrap = fonts.getHeightAndWrap(font_sm)
        wrapper = textwrap.TextWrapper(wrap)
        string = wrapper.wrap(text=format(
            psutil.cpu_times_percent(percpu=False)))
        v_height = (len(string) * height) + 2
        virtual = viewport(device, width=device.width, height=v_height)
        with canvas(virtual) as draw:
            for i, line in enumerate(string):
                draw.text((2, 0 + (i * height)), text=line,
                          font=font_sm, fill="white")
        sleep(3)
        for pos_y in range(v_height - (device.height)):
            virtual.set_position((0, pos_y))
            sleep(0.01)
    elif index == 8:
        #errors = os.popen('dmesg | grep oltage | wc -l').read()
        os.system('sudo cp /etc/wpa_supplicant/wpa_supplicant-wlan0.conf.save /etc/wpa_supplicant/wpa_supplicant-wlan0.conf')
        os.system('sudo cp /boot/config.txt.save /boot/config.txt')
        with canvas(device) as draw:
            #temps = psutil.sensors_temperatures()
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((2, 10), "Done", font=font, fill="white")
        #print(num)
    else:
        top_menu.init(3)

def draw_menu(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size = 11, icon_size = 12)

def cb_rotate(val):
    draw_menu(val)


def cb_switch(val):
    menu_operation(val % len(items))


def init(val):
    draw_menu(val)
    controls.init(__name__, val)
