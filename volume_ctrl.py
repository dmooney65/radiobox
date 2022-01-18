#!/usr/bin/env python3

import alsaaudio
#alsaaudio.Mixer
MIXER = alsaaudio.Mixer('Digital')
MAX_VOL = 79

def get_volume():
    return MIXER.getvolume()[0]


def set_volume(volume):
    MIXER.setvolume(volume)

def main():
    current_vol = get_volume()
    if current_vol < MAX_VOL:
        set_volume(current_vol + 1)

if __name__ == "__main__":
    main()

#def cb_bt_vol_down(dummy):
#    current_vol = get_volume()
#    if current_vol > 0:
#        set_volume(current_vol - 1)

