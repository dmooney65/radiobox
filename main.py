#!/usr/bin/python3

import sys
import os
import signal
import top_menu
import playing_menu
import queue_menu
import bt_player
import controls

def signal_handler(sig, frame):
    os.system('alsactl --file /home/pi/.config/asound.state store')
    print("\nexecuting\r\n")
    controls.reset_ts()
    os.system('../dabpi/dabpi_ctl -x')
    controls.cb_signal_handler(sig, frame)
    playing_menu.cb_signal_handler(sig, frame)
    queue_menu.cb_signal_handler(sig, frame)
    bt_player.cb_signal_handler(sig,frame)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    os.system('alsactl --file /home/pi/.config/asound.state restore')
    controls.reset_ts()
    top_menu.init(0)

if __name__ == "__main__":
    main()
