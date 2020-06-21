import os
from selectors import DefaultSelector, EVENT_READ
import evdev
import alsaaudio

MIXER = alsaaudio.Mixer('Digital')
MAX_VOL = 81
BT_CONTROLLER_PATH = '/dev/input/vr-control'

def cb_bt_mute():
    mute = MIXER.getmute()[0]
    if mute == 1:
        MIXER.setmute(0)
    else:
        MIXER.setmute(1)

def get_volume():
    return MIXER.getvolume()[0]

def set_volume(volume):
    MIXER.setvolume(volume)

def cb_bt_vol_up():
    current_vol = get_volume()
    if current_vol < MAX_VOL:
        set_volume(current_vol + 1)

def cb_bt_vol_down():
    current_vol = get_volume()
    if current_vol > 0:
        set_volume(current_vol - 1)

def handle_events(module, value):
    switch = evdev.InputDevice('/dev/input/by-path/platform-button@1b-event')
    rotate = evdev.InputDevice('/dev/input/by-path/platform-rotary@11-event')
    bt_controller = os.path.exists(BT_CONTROLLER_PATH)

    if bt_controller:
        bluetooth = evdev.InputDevice(BT_CONTROLLER_PATH)
    selector = DefaultSelector()

    selector.register(rotate, EVENT_READ)
    selector.register(switch, EVENT_READ)
    if bt_controller:
        selector.register(bluetooth, EVENT_READ)
    #for device in switch, rotate:
    while True:
        for key, dummy in selector.select():
            device = key.fileobj
        for event in device.read():
            event = evdev.util.categorize(event)
            if isinstance(event, evdev.events.RelEvent):
                value = value + event.event.value
                #print("rotate ev "+mod.__name__, value)
                module.cb_rotate(value)
            elif isinstance(event, evdev.events.KeyEvent):
                if event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                    #print("key ev "+mod.__name__, value)
                    module.cb_switch(value)
                elif event.keycode == "KEY_NEXTSONG" and event.keystate == event.key_up:
                    value = value + 1
                    try:
                        module.cb_bt_next(value)
                    except AttributeError as dummy:
                        module.cb_rotate(value)
                elif event.keycode == "KEY_PREVIOUSSONG" and event.keystate == event.key_up:
                    value = value - 1
                    try:
                        module.cb_bt_prev(value)
                    except AttributeError as dummy:
                        module.cb_rotate(value)
                elif event.keycode == "KEY_PLAYPAUSE" and event.keystate == event.key_up:
                    try:
                        module.cb_bt_play_pause(value)
                    except AttributeError as dummy:
                        module.cb_switch(value)
                elif event.keycode[1] == "KEY_MUTE" and event.keystate == event.key_up:
                    try:
                        module.cb_bt_mute(value)
                    except AttributeError as dummy:
                        cb_bt_mute()
                elif event.keycode == "KEY_VOLUMEUP" and event.keystate == event.key_up:
                    cb_bt_vol_up()
                elif event.keycode == "KEY_VOLUMEDOWN" and event.keystate == event.key_up:
                    cb_bt_vol_down()

def init(module, val):
    handle_events(module, val)
