
import os
import time
import ADS1x15
from RPi import GPIO
from evdev import UInput, ecodes as e
GPIO_ALERT = 16

print(os.path.basename(__file__))

uinput = UInput(name='stalk_ctl',
                events={
                    e.EV_KEY: [
                    e.KEY_ENTER,
                    e.KEY_PLAYPAUSE,
                    e.KEY_NEXTSONG,
                    e.KEY_PREVIOUSSONG,
                    e.KEY_VOLUMEDOWN,
                    e.KEY_VOLUMEUP
                    ],
                    e.EV_REL: [
                        e.REL_X
                    ]
                },
                devnode='/dev/uinput'
                )


class Comparator():
    ADS = None
    button = False
    flash = False
    ind_right = False
    ind_left = False
    centre = False
    #device = None

    def cb_int_both(self, channel):
        if GPIO.input(channel): #Rising edge
            raw = self.ADS.getValue()
            #print(raw)
            if raw > 1000:
                self.button = True
                self.flash = False
            elif raw > 800 and raw < 850:
                self.button = False
                self.flash = True
            else:
                self.button = False
                self.flash = False
            self.ADS.setMode(self.ADS.MODE_SINGLE)
            time.sleep(.01)
            right = self.ADS.readADC(0)
            left = self.ADS.readADC(1)
            if left > 1000:
                self.ind_left = True
                self.ind_right = False
                self.centre = False
            elif right > 1000:
                self.ind_left = False
                self.ind_right = True
                self.centre = False
            else:
                self.ind_left = False
                self.ind_right = False
                self.centre = True
            #print(right, left)
            if self.button:
                if self.ind_left:
                    #print('button, ind_left')
                    uinput.write(e.EV_REL, e.REL_X, -1)
                    uinput.syn()
                elif self.ind_right:
                    # print('button, ind_right')
                    uinput.write(e.EV_REL, e.REL_X, 1)
                    uinput.syn()
                else:
                    # print('button, default')
                    uinput.write(e.EV_KEY, e.KEY_ENTER, 1)
                    uinput.syn()
            elif self.flash:
                if self.ind_left:
                    # print('flash, ind_left')
                    uinput.write(e.EV_KEY, e.KEY_VOLUMEUP, 1)
                    uinput.syn()
                elif self.ind_right:
                    # print('flash, ind_right')
                    uinput.write(e.EV_KEY, e.KEY_VOLUMEDOWN, 1)
                    uinput.syn()
                else:
                    # print('flash, default')
                    uinput.write(e.EV_KEY, e.KEY_NEXTSONG, 1)
                    uinput.syn()
            self.ADS.setMode(self.ADS.MODE_CONTINUOUS)
            self.ADS.requestADC(3)
        else: # Falling edge
            if self.button:
                #if self.ind_left:
                #    pass
                    # print('button, ind_left')
                #elif self.ind_right:
                #    pass
                    # print('button, ind_right')
                if self.centre:
                    # print('button, default')
                    uinput.write(e.EV_KEY, e.KEY_ENTER, 0)
                    uinput.syn()
            elif self.flash:
                if self.ind_left:
                    uinput.write(e.EV_KEY, e.KEY_VOLUMEUP, 0)
                    uinput.syn()
                elif self.ind_right:
                    uinput.write(e.EV_KEY, e.KEY_VOLUMEDOWN, 0)
                    uinput.syn()
                else:
                    uinput.write(e.EV_KEY, e.KEY_NEXTSONG, 0)
                    uinput.syn()

    def __init__(self):
        self.ADS = ADS1x15.ADS1015(1, 0x48)
        # Setup GPIO to ALRT pin
        GPIO.setmode(GPIO.BCM)
        #GPIO.cleanup(GPIO_ALERT)
        GPIO.setup(GPIO_ALERT, GPIO.IN)
        GPIO.add_event_detect(GPIO_ALERT, GPIO.BOTH,
                              callback=self.cb_int_both)
        self.ADS.setGain(self.ADS.PGA_4_096V)
        self.ADS.setDataRate(self.ADS.DR_ADS101X_1600)
        # set comparator to traditional mode, active high, latch, and trigger alert after 4 conversions
        self.ADS.setComparatorMode(self.ADS.COMP_MODE_TRADITIONAL)
        self.ADS.setComparatorPolarity(self.ADS.COMP_POL_ACTIV_HIGH)
        self.ADS.setComparatorLatch(self.ADS.COMP_LATCH)
        self.ADS.setComparatorQueue(self.ADS.COMP_QUE_4_CONV)
        self.ADS.setComparatorThresholdLow(700)
        self.ADS.setComparatorThresholdHigh(800)
        self.ADS.setMode(self.ADS.MODE_CONTINUOUS)
        self.ADS.requestADC(3)

    def __del__(self):
        GPIO.cleanup(GPIO_ALERT)

COMP = None 

while True:
    if COMP is None:
        try:
            COMP = Comparator()
        except OSError as e:
            pass
    time.sleep(2)
