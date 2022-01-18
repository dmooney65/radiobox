# coding: utf-8

from time import sleep

import RPi.GPIO as GPIO
import spidev
import constants
import utils
from fm_classes import RsqStatus, RDS
from dab_classes import ServiceList, Ensemble, Status
import encoding
from dab_db import DABDatabase

GPIO_RESET = 23
GPIO_INTB = 25

keys0 = ["CTS", "ERR_CMD", "DACQINT", "DSRVINT",
         "RSQINT", "RDSINT", "ACFINT", "STCINT"]


class Radio():
    _instance = None
    spi = None
    dicti0 = {}
    listener = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Radio, cls).__new__(cls)
        return cls._instance

    def cb_int_falling(self, channel):  # , *args, **kwargs):
        #print("Interrupt falling")
        data = self.spi.readbytes(6)
        #print('rd_reply ', format(data))
        values0 = utils.get_bitlist(data[1])
        self.dict0 = dict(zip(keys0, values0))
        # print(values0)
        if self.listener:
            self.listener(self.dict0)  # , *args, **kwargs)

    def __init__(self, bus=0, device=0):
        self._instance = 1
        print('init radio')
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 6000000
        self.spi.mode = 0b00
        self.spi.bits_per_word = 8
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup(GPIO_INTB)
        GPIO.setup(GPIO_INTB, GPIO.IN)  # , pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(GPIO_INTB, GPIO.FALLING,
                              callback=self.cb_int_falling)
        

    def __del__(self):
        print('radio del')
        GPIO.setmode(GPIO.BCM)
        # GPIO.remove_event_detect(GPIO_INTB)
        GPIO.cleanup(GPIO_INTB)
        self._instance = None

    def set_property(self, name, value):
        print('set property')
        req = []
        req.extend([constants.SET_PROPERTY, 0, name & 0xFF,
                    (name >> 8) & 0xFF, value & 0xFF, (value >> 8) & 0xFF])
        self.spi.writebytes(req)
        sleep(.1)
        self.get_property(name)
        sleep(.1)
        data = self.spi.readbytes(7)
        val = data[5] & 0xFF | (data[6] >> 8) & 0xFF
        print(data)
        timeout = 0
        if val != value and not timeout > 50:
            print('timeout {}'.format(timeout))
            self.get_property(name)
            sleep(.1)
            data = self.spi.readbytes(7)
            print(data)
            val = data[5] & 0xFF | (data[6] >> 8) & 0xFF
            timeout += 1

    def get_property(self, name):
        req = []
        req.extend([constants.GET_PROPERTY, 1,
                    name & 0xFF, (name >> 8) & 0xFF])
        self.spi.writebytes(req)


class FM():
    radio = None
    rsq_status = None
    rds = None
    command = constants.RD_REPLY
    listener = None

    def __init__(self, bus=0, device=0):
        print('init fm')
        if not self.radio:
            self.radio = Radio()
        self.radio.set_property(constants.INT_CTL_ENABLE, 0x008D)
        self.radio.listener = self.cb_int_listener

    def __del__(self):
        print('deleting fm')
        self.remove_listeners()
        self.radio = None

    def cb_int_listener(self, event):
        notify = True
        if event.get('STCINT') == 1:
            self.rsq_status = None
            self.get_rsq_status()
            self.rds = RDS()
        elif event.get('RDSINT') == 1 and event.get('STCINT') == 0:
            if not self.rds:
                # if not self.rds.complete
                sleep(.1)
                self.get_rds_status()
            elif not self.rds.complete:
                sleep(.1)
                self.get_rds_status()
        elif event.get('STCINT') == 0 and self.command == constants.FM_RSQ_STATUS:  # STC acknowledged
            print('RSQ listener called')
            # sleep(0.01)
            data = self.radio.spi.readbytes(23)
            self.rsq_status = RsqStatus(data)
            self.count = 1
            # self.get_rds_blockcount()
            self.command = constants.RD_REPLY
        elif event.get('STCINT') == 0 and self.command == constants.FM_RDS_STATUS:  # STC acknowledged
            #print('RDS listener called')
            sleep(0.05)
            data = self.radio.spi.readbytes(21)
            self.rds.process(data)
            if self.rds.size > 1 and not self.rds.complete:
                # sleep(.1)
                self.get_rds_status()
            elif self.rds.complete:
                self.command = constants.RD_REPLY
        else:
            notify = False
            self.command = constants.RD_REPLY

        if notify:
            if self.listener:
                self.listener(event)

    def add_listener(self, listener):
        #self.radio.set_property(constants.INT_CTL_ENABLE, 0x008D)
        # sleep(0.1)
        self.radio.listener = self.cb_int_listener
        self.listener = listener
        # return self

    def remove_listeners(self):
        # print('deleting')
        self.radio.listener = None
        self.listener = None

    def read_reply(self, size=6):
        self.radio.spi.writebytes([constants.RD_REPLY])

    def read_bytes(self, size=6):
        return self.radio.spi.readbytes(size)

    def seek_up(self):
        self.radio.spi.writebytes(
            [constants.FM_SEEK_START, 0x00, 0x03, 0x00, 0x00, 0x00])

    def seek_down(self):
        self.radio.spi.writebytes(
            [constants.FM_SEEK_START, 0x00, 0x01, 0x00, 0x00, 0x00])

    def get_rsq_status(self):
        self.radio.spi.writebytes([constants.FM_RSQ_STATUS, 0x01])
        self.command = constants.FM_RSQ_STATUS

    def tune_freq(self, freq):
        self.radio.spi.writebytes(
            [constants.FM_TUNE_FREQ, 0x00, freq & 0xFF, (freq >> 8) & 0xFF, 0x00, 0x00, 0x00])

    def get_rds_status(self):
        #print('rds called')
        if self.command is not constants.FM_RSQ_STATUS:  # Prioritise RSQ
            self.command = constants.FM_RDS_STATUS
            self.radio.spi.writebytes([constants.FM_RDS_STATUS, 0x01])

    def get_rds_blockcount(self):
        self.radio.spi.writebytes([constants.FM_RDS_BLOCKCOUNT, 0x00])


class DAB():
    radio = None
    status = None
    srv_list_size = 0
    command = constants.RD_REPLY
    listener = None
    frequencies = []
    service_list = None
    ensembles = None

    def __init__(self, bus=0, device=0):
        print('init dab')
        if not self.radio:
            self.radio = Radio()
        self.radio.set_property(constants.INT_CTL_ENABLE, 0x00F1)
        self.radio.listener = self.cb_int_listener
        sleep(.1)
        self.set_frequency_list()
        self.ensembles = []

    def __del__(self):
        print('deleting dab')
        self.remove_listener()
        self.remove_radio_listener()
        self.radio = None

    def cb_int_listener(self, event):
        notify = False
        notify_string = None
        #print('int happened {}'.format(hex(self.command)))
        #print(event)
        # if event.get('ERR_CMD') == 1:
        #    print('error')

        if event.get('STCINT') == 1:
            if self.command == constants.DAB_TUNE_FREQ:
                self.status = None
                #print('stc tune')
                self.get_digrad_status()

        elif event.get('STCINT') == 0 and event.get("DSRVINT") == 0:
            if self.command == constants.DAB_SET_FREQ_LIST:
                #print('freq list')
                self.command = constants.RD_REPLY
            elif self.command == constants.DAB_DIGRAD_STATUS:
                #print('stc digrad status')
                data = self.radio.spi.readbytes(23)
                self.status = Status(data)
                notify = True
                notify_string = 'status'
                print(self.status.acq)
                self.command = constants.RD_REPLY
            elif self.command == constants.DAB_GET_ENSEMBLE_INFO:
                # print('ensembles')
                # sleep(1)
                if event.get('ERR_CMD') == 1:
                    self.radio.spi.writebytes([constants.RD_REPLY])
                else:
                    ensemble = self.read_ensemble()
                    if ensemble.label is None:
                        sleep(0.1)
                        self.get_ensemble_info()
                    else:
                        self.ensembles.append(ensemble)
                        notify = True
                        notify_string = 'ensemble'
                        self.command = constants.RD_REPLY

            elif self.command == constants.GET_DIGITAL_SERVICE_LIST:
                sleep(0.5)
                data = self.radio.spi.readbytes(7)
                size = data[6] << 8 | data[5]
                #print('size {}'.format(size))
                if size > 0:
                    if self.srv_list_size < size:
                        #print('size if')
                        self.srv_list_size = size
                        print(self.srv_list_size)
                        sleep(0.5)
                        self.get_digital_service_list()
                    else:
                        #print('size else')
                        data = self.radio.spi.readbytes(7 + size)
                        num_services = data[9]
                        print('services ={}'.format(num_services))

                        s_list = ServiceList(data)
                        print('data 21 =', chr(data[21]))
                        if s_list.success:
                            self.service_list = s_list
                            notify = True
                            notify_string = 'services'
                            self.command = constants.RD_REPLY
                        else:
                            sleep(0.2)
                            self.get_digital_service_list()

            if self.command == constants.GET_DIGITAL_SERVICE_DATA:
                sleep(.1)
                data = self.radio.spi.readbytes(25)
                # print(data[19])
                # self.radio.spi.writebytes([constants.RD_REPLY])
                sleep(.1)
                data = self.radio.spi.readbytes(25+data[19])
                print('msg type {}'.format(data[25]))  # 128= Now Playing??
                data_in = data[27:]
                text = encoding.decode_text(data_in)
                print(text)
                self.command = constants.RD_REPLY

        # and not self.command == constants.GET_DIGITAL_SERVICE_DATA:
        elif event.get("DSRVINT") == 1:
            self.get_digital_service_data()
        else:
            print('int ignored')
            self.command = constants.RD_REPLY
        if notify and self.listener:
            self.listener(notify_string)
            notify = False
            notify_string = None

    def scan(self):
        self.ensembles = []
        db = DABDatabase()
        db.clear_ensembles()
        for i in range(len(self.frequencies)):
            print('tuning {}'.format(i))
            self.tune_frequency(i)
            # sleep(0.1)
            while not self.status:
                # print('while')
                sleep(0.1)
            else:
                # print('else')
                if self.status.acq == 1:
                    #print('acq 1')
                    #self.command = constants.RD_REPLY
                    sleep(0.2)
                    self.get_ensemble_info()
                    while self.command is constants.DAB_GET_ENSEMBLE_INFO:
                        #print('while command')
                        self.get_ensemble_info()
                        sleep(0.1)
                # else:
                #    print('acq 0')
                self.status = None
        self.status = None

        for ensemble in self.ensembles:
            db.add_ensemble(ensemble)
        db.get_ensembles()
        self.listener('ensembles')

    def read_ensemble(self):
        data = self.radio.spi.readbytes(27)
        ensemble = Ensemble(data, self.status)
        print(ensemble.label)
        return ensemble

    def add_listener(self, listener):
        #self.radio.set_property(constants.INT_CTL_ENABLE, 0x00F1)
        # sleep(.5)
        self.radio.listener = self.cb_int_listener
        self.listener = listener
        # return self

    def remove_listener(self):
        self.listener = None

    def remove_radio_listener(self):
        self.radio.listener = None

    def set_frequency_list(self, freq_list=constants.UK_CHANNELS):
        self.command = constants.DAB_SET_FREQ_LIST
        for i in freq_list:
            self.frequencies.append(constants.DAB_CHANNELS.get(i))

        req = []
        req.extend([constants.DAB_SET_FREQ_LIST, len(self.frequencies), 0, 0])
        for i in self.frequencies:
            req.extend([i & 0xFF, i >> 8, i >> 16, i >> 24])
        self.radio.spi.writebytes(req)

    def tune_frequency(self, freq_index):
        print('tuning {}'.format(freq_index))
        req = []
        req.extend([constants.DAB_TUNE_FREQ, 0, freq_index, 0, 0, 0])
        timeout = 0
        while self.command is constants.DAB_SET_FREQ_LIST and not timeout > 0:
            print('sleeping')
            sleep(0.1)
            timeout += 1
        else:
            print('else')
            self.command = constants.DAB_TUNE_FREQ
            self.radio.spi.writebytes(req)

    def get_ensemble_info(self):
        req = [constants.DAB_GET_ENSEMBLE_INFO, 0]
        timeout = 0
        while self.command == constants.DAB_DIGRAD_STATUS and not timeout > 10:
            sleep(0.1)
            timeout += 1
        else:
            self.command = constants.DAB_GET_ENSEMBLE_INFO
            self.radio.spi.writebytes(req)
        # self.radio.spi.writebytes(req)

    def get_digrad_status(self):
        self.command = constants.DAB_DIGRAD_STATUS
        req = [constants.DAB_DIGRAD_STATUS, 1]
        self.radio.spi.writebytes(req)

    def get_digital_service_list(self):
        self.service_list = None
        self.command = constants.GET_DIGITAL_SERVICE_LIST
        req = []
        req.extend([constants.GET_DIGITAL_SERVICE_LIST, 0x00])
        self.radio.spi.writebytes(req)

    def start_digital_service(self, service_id, component_id):
        self.command = constants.START_DIGITAL_SERVICE
        req = []
        req.extend([constants.START_DIGITAL_SERVICE, 0, 0, 0,
                    service_id & 0xFF, (service_id >>
                                        8) & 0xFF, (service_id >> 16) & 0xFF,
                    (service_id >> 24) & 0xFF, component_id & 0xFF, (component_id >> 8) & 0xFF,
                    (component_id >> 16) & 0xFF, (component_id >> 24) & 0xFF])
        self.radio.spi.writebytes(req)

    def stop_digital_service(self, service_id, component_id):
        self.command = constants.STOP_DIGITAL_SERVICE
        req = []
        req.extend([constants.STOP_DIGITAL_SERVICE, 0, 0, 0,
                    service_id & 0xFF, (service_id >>
                                        8) & 0xFF, (service_id >> 16) & 0xFF,
                    (service_id >> 24) & 0xFF, component_id & 0xFF, (component_id >> 8) & 0xFF,
                    (component_id >> 16) & 0xFF, (component_id >> 24) & 0xFF])
        self.radio.spi.writebytes(req)

    def get_digital_service_data(self):
        self.command = constants.GET_DIGITAL_SERVICE_DATA
        req = []
        req.extend([constants.GET_DIGITAL_SERVICE_DATA, 1])
        self.radio.spi.writebytes(req)
