from atexit import register
from curses import can_change_color
import os
import sys
from time import time
from selectors import DefaultSelector, EVENT_READ
from evdev import ecodes, InputDevice, UInput, util, events, list_devices
#import alsaaudio
from timer import InfiniteTimer
from display import Oled
from state import State

#BT_CONTROLLER_PATH = '/dev/input/bt-control'
state = State()
HIDDEN = False
TS = time()

# Keep BT controller persistent. Relies on triggerhappy service
uinput = UInput(name='virt_bt',
            events={
                 ecodes.EV_KEY: [
                     ecodes.KEY_HOME,
                     ecodes.KEY_PLAY,
                     ecodes.KEY_NEXT, 
                     ecodes.KEY_PREVIOUS,
                     ecodes.KEY_CONTEXT_MENU
                 ]
            },
            devnode='/dev/uinput'
        )


def show():
    display = Oled().get_device()
    display.show()


def hide():
    display = Oled().get_device()
    display.hide()

def cancel_timer():
    if state.timer is not None:
        state.timer.cancel()

def cb_signal_handler(sig, frame):
    print("controls timer exiting gracefully")
    cancel_timer()

def reset_ts():
    global TS
    global HIDDEN
    TS = time()
    HIDDEN = False


def tick():
    global TS
    global HIDDEN
    now = time()
    if now - TS > 900:
        if not HIDDEN:
            HIDDEN = True
            hide()
    else:
        if HIDDEN:
            show()
            HIDDEN = False

def handle_events(module, value):
    global TS
    #selector = DefaultSelector()
    selector = DefaultSelector()
    #for d in list_devices():
    #    selector.register(InputDevice(d), EVENT_READ)
    #pass
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if device.name == 'virt_bt':
            selector.register(device, EVENT_READ)
    selector.register(InputDevice('/dev/input/by-path/platform-button@11-event'), EVENT_READ)
    selector.register(InputDevice('/dev/input/by-path/platform-rotary@16-event'), EVENT_READ)
    

    prev_stamp = 0

    while True:
        for key, dummy in selector.select():
            device = key.fileobj
        try:
            for event in device.read():
                TS = event.timestamp()
                event = util.categorize(event)
                if isinstance(event, events.RelEvent):
                    value = value + event.event.value
                    module.cb_rotate(value)
                elif isinstance(event, events.KeyEvent):
                    if event.keycode == "KEY_ENTER" and event.keystate == event.key_down:
                        prev_stamp = event.event.timestamp()
                    elif event.keycode == "KEY_HOME" and event.keystate == event.key_down:
                        cancel_timer()
                        module.cb_switch(0)
                    elif event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                        if 'dab_ensembles' not in str(module.__file__):
                            cancel_timer()
                        if hasattr(module, 'cb_long_press') \
                            and event.event.timestamp() - prev_stamp > 0.6:
                            module.cb_long_press(value)
                        else:
                            module.cb_switch(value)
                    elif event.keycode == "KEY_NEXT" and event.keystate == event.key_up:
                        value = value + 1
                        if hasattr(module, 'cb_bt_next'):
                            module.cb_bt_next()
                        else:
                            module.cb_rotate(value)
                    elif event.keycode == "KEY_PREVIOUS" and event.keystate == event.key_up:
                        value = value - 1
                        if hasattr(module, 'cb_bt_prev'):
                            module.cb_bt_prev()
                        else:
                            module.cb_rotate(value)
                    elif event.keycode == "KEY_PLAY" and event.keystate == event.key_up:
                        if 'dab_ensembles' not in str(module.__file__):
                            cancel_timer()
                        if hasattr(module, 'cb_bt_play_pause'):
                            module.cb_bt_play_pause()
                        else:
                            module.cb_switch(value)
                    elif event.keycode == "KEY_CONTEXT_MENU" and event.keystate == event.key_up:
                        if hasattr(module, 'cb_long_press'):
                            module.cb_long_press(value)

        except OSError as e:
            # Throws error when bt device is removed so have to re-register all
            print(e)
            selector = DefaultSelector()
            for d in list_devices():
                selector.register(InputDevice(d), EVENT_READ)
            pass
        #finally:
            



def init(module, val):
    state.timer = InfiniteTimer(1, tick)
    state.timer.start()
    handle_events(__import__(module), val)
