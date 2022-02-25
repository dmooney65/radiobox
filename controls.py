#from atexit import register
#from curses import can_change_color
import os
import sys
from time import time
from selectors import *
from evdev import ecodes, InputDevice, util, events, list_devices
from timer import InfiniteTimer
from display import Oled
from state import State
from select import select
import volume_ctrl

# BT_CONTROLLER_PATH = '/dev/input/bt-control'
state = State()
HIDDEN = False
TS = time()

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

def get_devices():
    device_list = [InputDevice(path) for path in list_devices()]
    devices = []
    vr_control = False
    for device in device_list:
        if device.name == 'button@11':
            devices.append(InputDevice(device))
        elif device.name == 'rotary@16':
            devices.append(InputDevice(device))
        elif device.name == 'stalk_ctl':
            devices.append(InputDevice(device))
        elif device.name == 'VR Remote Control Consumer Control':
            vr_control = True
            devices.append(InputDevice(device))
    return devices, vr_control
    
def handle_events(module, value):
    global TS
    ev_state = {}
    devices, vr_control = get_devices()
    devices = {dev.fd: dev for dev in devices}

    while True:
        if not vr_control and os.path.exists('/dev/input/vr-control'):
                devices, vr_control =  get_devices()
                devices = {dev.fd: dev for dev in devices}
        r, _, _ = select(devices, [], [], 0.1)
        try:
            for fd in r:
                for event in devices[fd].read():
                    TS = event.timestamp()
                    event = util.categorize(event)
                    if isinstance(event, events.RelEvent):
                        value = value + event.event.value
                        module.cb_rotate(value)
                    elif isinstance(event, events.KeyEvent):
                        if event.keycode == "KEY_ENTER" and event.keystate == event.key_down:
                            ev_state[event.event.code] = event.event.timestamp(), event
                        if event.keycode == "KEY_NEXTSONG" and event.keystate == event.key_down:
                            ev_state[event.event.code] = event.event.timestamp(), event
                        elif event.keycode == "KEY_VOLUMEDOWN" and event.keystate == event.key_down:
                            ev_state[event.event.code] = event.event.timestamp(), event
                        elif event.keycode == "KEY_VOLUMEUP" and event.keystate == event.key_down:
                            ev_state[event.event.code] = event.event.timestamp(), event
                        elif event.keycode == "KEY_HOME" and event.keystate == event.key_down:
                            cancel_timer()
                            module.cb_switch(0)
                        elif event.keycode == "KEY_ENTER" and event.keystate == event.key_up:
                            if event.event.code in ev_state:
                                ev_state[event.event.code] = event.event.timestamp(), event
                            if 'dab_ensembles' not in str(module.__file__):
                                cancel_timer()
                        elif event.keycode == "KEY_NEXTSONG" and event.keystate == event.key_up:
                            if event.event.code in ev_state:
                                ev_state[event.event.code] = event.event.timestamp(), event
                        elif event.keycode == "KEY_PREVIOUSSONG" and event.keystate == event.key_up:
                            if hasattr(module, 'cb_bt_prev'):
                                module.cb_bt_prev()
                            else:
                                value = value - 1
                                module.cb_rotate(value)
                        elif event.keycode == "KEY_PLAYPAUSE" and event.keystate == event.key_up:
                            if 'dab_ensembles' not in str(module.__file__):
                                cancel_timer()
                            if hasattr(module, 'cb_bt_play_pause'):
                                module.cb_bt_play_pause()
                            else:
                                module.cb_switch(value)
                        elif event.keycode == "KEY_CONTEXT_MENU" and event.keystate == event.key_up:
                            if hasattr(module, 'cb_long_press'):
                                module.cb_long_press(value)
                        elif event.keycode == "KEY_VOLUMEDOWN" and event.keystate == event.key_up:
                            if event.event.code in ev_state:
                                ev_state[event.event.code] = event.event.timestamp(), event
                        elif event.keycode == "KEY_VOLUMEUP" and event.keystate == event.key_up:
                            if event.event.code in ev_state:
                                ev_state[event.event.code] = event.event.timestamp(), event
                        elif event.keycode[1] == "KEY_MUTE" and event.keystate == event.key_up:
                            volume_ctrl.mute_toggle()

            now = time()
            for code, ts_event in list(ev_state.items()):
                #print(ev_state)
                ts, event = ts_event
                #print(ts)
                if (now - ts) >= 0.5:
                    del ev_state[code]  # only trigger once
                    if event.keycode == "KEY_ENTER":
                        if hasattr(module, 'cb_long_press'):
                            module.cb_long_press(value)
                        else:
                            cancel_timer()
                            module.cb_switch(0)
                    elif event.keycode == "KEY_NEXTSONG":
                        if hasattr(module, 'cb_bt_prev'):
                            module.cb_bt_prev()
                        else:
                            value = value - 1
                            module.cb_rotate(value)
                    elif event.keycode == "KEY_VOLUMEDOWN":
                        volume_ctrl.cb_bt_vol(-5)
                    elif event.keycode == "KEY_VOLUMEUP":
                        volume_ctrl.cb_bt_vol(5)
                elif event.keystate == event.key_up:
                    del ev_state[code]
                    if event.keycode == "KEY_ENTER":
                        module.cb_switch(value)
                    elif event.keycode == "KEY_NEXTSONG":
                        if hasattr(module, 'cb_bt_next'):
                            module.cb_bt_next()
                        else:
                            value = value + 1
                            module.cb_rotate(value)
                    elif event.keycode == "KEY_VOLUMEDOWN":
                        volume_ctrl.cb_bt_vol(-1)
                    elif event.keycode == "KEY_VOLUMEUP":
                        volume_ctrl.cb_bt_vol(1)
                
            continue
        except OSError as e:
            # Throws error when bt device is removed so have to re-register all
            print(e)
            devices, vr_control = get_devices()
            devices = {dev.fd: dev for dev in devices}
            pass


def init(module, val):
    state.timer = InfiniteTimer(0.5, tick)
    state.timer.start()
    handle_events(__import__(module), val)
