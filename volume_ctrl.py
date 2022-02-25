
import alsaaudio
MIXER = alsaaudio.Mixer('Digital')
MAX_VOL = 79
#MIN_VOL = 

def get_volume():
    return MIXER.getvolume()[0]

def mute_toggle():
    if MIXER.getmute()[0] == 0:
        MIXER.setmute(1)
    else:
        MIXER.setmute(0)

def set_volume(volume):
    MIXER.setvolume(volume)

#def main():
    #current_vol = get_volume()
    #if current_vol < MAX_VOL:
    #    set_volume(current_vol + 1)

#if __name__ == "__main__":
#    main()

def cb_bt_vol(val):
    MIXER.setmute(0)
    current_vol = get_volume()
    if current_vol + val <= 0:        
        if val >= 0:
            set_volume(current_vol + val)
        else:
            set_volume(0)
    elif current_vol + val < MAX_VOL:
        set_volume(current_vol + val)
    else:
        set_volume(MAX_VOL)

def cb_mute():
    mute_toggle()
