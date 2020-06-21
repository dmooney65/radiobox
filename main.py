# -*- encoding: utf-8 -*-

import sys
import signal
import alsaaudio

import top_menu
import playing_menu
#import fonts
from classes import Oled

def signal_handler(sig, frame):
    playing_menu.cb_signal_handler(sig, frame)
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main():
    volume = alsaaudio.Mixer('Digital')
    volume.setmute(0)
    volume.setvolume(81)
    Oled().get_device().contrast(128)
    top_menu.init(0)

if __name__ == "__main__":
    main()
