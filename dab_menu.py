from time import sleep
from luma.core.render import canvas
from PIL import ImageFont

#import encoding
import controls
import fonts
import menu
import dab_ensembles
from display import Oled
#from radio import DAB

device = Oled().get_device()
dab = None
VALUE = 0

items_service = [(fonts.menu_up, 'Back')]
font = ImageFont.truetype(fonts.font_default, size=12)
font_sm = ImageFont.truetype(fonts.font_default, size=10)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)


def menu_up():
    if controls.state.timer:
        controls.state.timer.cancel()
    global dab
    dab = None
    dab_ensembles.redraw()

def menu_operation(index):
    print(index)
    if index == 0:
        menu_up()
    else:
        if items_service[index][0] is fonts.pause:
            item = items_service[index]
            dab.stop_digital_service(item[2], item[3])
            items_service[index] = ('',item[1], item[2], item[3])
            draw_menu()
        else:
            for i in  range(len(items_service)):
                if items_service[i][0] is fonts.pause:
                    item = items_service[i]
                    items_service[i] = ('', item[1], item[2], item[3])
            item = items_service[index]
            dab.start_digital_service(item[2], item[3])
            items_service[index] = (fonts.pause,item[1], item[2], item[3])
            draw_menu()

def draw_menu():
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items_service, VALUE % len(items_service), font_size = 11, icon_size = 12)

def cb_rotate(val):
    global VALUE
    VALUE = val
    draw_menu()

def cb_switch(val):
    global VALUE
    VALUE = val
    menu_operation(val % len(items_service))

def cb_dab_event(event):
    if dab:
        global items_service
        if event == 'status':
            if dab.status.acq == 1:
                dab.get_digital_service_list()
        if event == 'services':
            if dab.service_list.services:
                items_service = []
                items_service.append((fonts.menu_up, 'Back'))
                for service in dab.service_list.services:
                    #print(service.srv_link_flag)
                    if(service.prog_type == 0):
                        items_service.append(('',service.service_label, service.service_id, service.components[0]))
                draw_menu()

def init(index, dab_instance):
    global dab
    dab = dab_instance
    global VALUE
    #global items_service
    #items_service = [(fonts.menu_up, 'Back')]
    VALUE = 0
    dab.add_listener(cb_dab_event)
    sleep(.1)
    dab.tune_frequency(index)
    with canvas(device) as draw:
        draw.text((5, 10), "DAB: Tuning...", font=font, fill="white")
    controls.init(__name__, VALUE)
