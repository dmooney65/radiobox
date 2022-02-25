from time import sleep
from math import floor
#import string
from luma.core.render import canvas
from PIL import ImageFont
import textwrap
#import encoding
import controls
import fonts
import menu
import dab_options
from display import Oled
from radio import DAB
from dab_db import DABDatabase

device = Oled().get_device()
#dab = None
#VALUE = 0
db = DABDatabase()


font = ImageFont.truetype(fonts.font_default, size=12)
font_fixed = ImageFont.truetype(fonts.font_default, size=10)
#font_fixed = ImageFont.truetype(fonts.font_fixed, size=10)
font_tiny = ImageFont.truetype(fonts.font_tiny, size=10)
icon = ImageFont.truetype(fonts.font_icon, size=fonts.size_default)


class State:
    value = 0
    dab = None
    ensembles = []
    services = []
    option = None
    items = []
    station = None

    def set_station(self, index):
        self.station = self.items[index]


state = State()


def menu_up():
    if controls.state.timer:
        controls.state.timer.cancel()
    state.dab.remove_radio_listener()
    state.dab.remove_listener()
    state.dab = None
    state.station = None
    if state.option == 'favourites':
        dab_options.init(1)
    else:
        dab_options.init(2)


def menu_operation(index):
    #size = len(items)
    if index == 0:
        menu_up()
    else:
        if state.items[index][0] is fonts.pause:
            item = state.items[index]
            state.dab.stop_digital_service(item[2], item[3])
            state.items[index] = ('', item[1], item[2], item[3], item[4])
            draw_menu()
        else:
            for i in range(len(state.items)):
                if state.items[i][0] is fonts.pause:
                    item = state.items[i]
                    state.items[i] = ('', item[1], item[2], item[3], item[4])
            if state.station is not None:
                if state.station[4] == state.items[index][4]:
                    state.dab.start_digital_service(
                        state.items[index][2], state.items[index][3])
                    sleep(0.1)
                else:
                    state.dab.tune_frequency(state.items[index][4])
                    sleep(0.1)
            else:
                state.dab.tune_frequency(state.items[index][4])
            state.set_station(index)
            print(state.station)
            state.items[index] = (fonts.pause, state.station[1],
                                  state.station[2], state.station[3], state.station[4])
            draw_menu()


def draw_menu(data=False):
    with canvas(device) as draw:
        if state.dab.service_data is not None and state.dab.audio_info is not None and data is True:
            controls.reset_ts()
            height_wrap = fonts.getHeightAndWrap(
                font_fixed, state.dab.service_data)
            height = height_wrap[0]
            wrapper = textwrap.TextWrapper(height_wrap[1])
            string = wrapper.wrap(state.dab.service_data)
            audio_info = state.dab.audio_info
            if audio_info.sbr > 0:
                dab_state = 'DAB+ '
            else:
                dab_state = 'DAB '
            if audio_info.audio_mode == 1:
                if audio_info.ps > 0:
                    mode = 'Stereo '
                else:
                    mode = 'Mono '
            elif audio_info.audio_mode == 2:
                mode = 'Stereo '
            else:
                mode = 'Joint Stereo '

            draw.text((1, 56), dab_state + mode + format(audio_info.bitrate) + 'k/s ' +
                      format(floor(audio_info.samplerate/1000)) + 'kHz ', font=font_tiny, fill="white")
            for i, line in enumerate(string):
                if i < 5:
                    draw.text((2, 3 + (i * (height-1))), text=format(line).strip(),
                              font=font_fixed, fill="white")
        else:
            menu.draw_menu(device, draw, state.items, state.value %
                           len(state.items), font_size=11, icon_size=11)


def now_playing(draw):
    draw.text((5, 10), "DAB: Scanning...", font=font, fill="white")


def cb_rotate(val):
    state.dab.service_data = None
    state.value = val
    draw_menu()


def cb_switch(val):
    state.dab.service_data = None
    state.value = val
    menu_operation(state.value % len(state.items))


def cb_long_press(val):
    if val % len(state.items) != 0:
        value = val % len(state.items) - 1
        if state.option == 'all':
            item = state.items[value + 1]
            rows = db.get_favourite(state.services[value])
            if len(rows) == 0:
                db.add_favourite(state.services[value])
                state.items[value + 1] = (fonts.star, item[1],
                                          item[2], item[3], item[4])
            else:
                db.remove_favourite(state.services[value])
            create_items()
        elif state.option == 'favourites':
            db.remove_favourite(state.services[value])
            create_items()
    else:
        menu_up()


def cb_dab_event(event):
    if state.dab is not None:
        if event == 'status':
            if state.option != 'rescan':
                state.dab.get_ensemble_info()
        elif event == 'ensemble':
            if state.option != 'rescan':
                state.dab.start_digital_service(
                    state.station[2], state.station[3])
                sleep(0.1)
        elif event == 'service_start':
            sleep(0.5)
            state.dab.get_audio_info()
        elif event == 'ensembles':
            state.option = 'all'
            create_items()
            draw_menu()
        elif event == 'service_data':
            sleep(2)
            draw_menu(True)


def create_items():
    ensembles = db.get_ensembles()
    if len(ensembles) == 0 or state.option == 'rescan':
        state.option = 'rescan'
        state.dab.scan()
    else:
        state.ensembles = ensembles
        state.items = []
        state.items.append((fonts.menu_up, 'Back'))
        if state.option == 'favourites':
            state.services = db.get_favourites()
            for service in state.services:
                state.items.append(
                    ('', service[7], service[0], service[1], service[8]))
        else:
            state.services = db.get_services()
            for service in state.services:
                fav = db.get_favourite(service)
                icon = ''
                if len(fav) > 0:
                    icon = fonts.star
                state.items.append(
                    (icon, service[7], service[0], service[1], service[8]))
        draw_menu()


def init(option, val):
    state.dab = DAB()
    state.value = val
    state.option = option
    state.dab.add_listener(cb_dab_event)
    sleep(.1)
    with canvas(device) as draw:
        now_playing(draw)
    create_items()
    controls.init(__name__, val)
