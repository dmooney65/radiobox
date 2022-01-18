import re
from ctypes import c_byte

import utils
import constants

class RsqStatus():
    frequency = 0
    snr = 0
    rssi = 0
    freq_offset = 0
    antcap = 0

    def __init__(self, data):
        self.frequency = (data[8] << 8 | data[7])
        self.snr = data[11]
        self.rssi = data[10]
        self.freq_offset = c_byte(data[9] * 2).value
        self.antcap = data[13]

class RDS():
    fail_count = 0
    groups = None
    pi = 0
    size = 0
    sync = 0
    complete = False
    group = 0
    pty = 0
    name = None
    radio_text = None
    ps = None
    rt = None

    def __init__(self):
        self.ps = [None]*4
        self.rt = [None]*16
        self.groups = []
        self.addrs = []

    def process(self, data):
        resp5 = utils.get_bitlist(data[6])
        self.sync = resp5[6]
        if self.sync == 1:  # Check Sync
            self.size = data[11]

            self.pi = data[9] | data[10] << 8
            # blocks=[]
            pty_int = utils.get_int(utils.get_bitlist(data[7])[3:])
            self.pty = constants.PTY_TYPES[pty_int]

            #blocks.append(hex(data[13] + (data[14] << 8)))
            block_b = data[15] + (data[16] << 8)
            #blocks.append(data[17] + (data[18] << 8))
            #blocks.append(data[19] + (data[20] << 8))

            self.group = block_b >> 12

            if self.group not in self.groups:
                self.groups.append(self.group)
                print('add group ' + str(self.group))

            if self.group == 0 and data[19] > 0 and self.name is None:
                addr = block_b & 0x03

                self.ps[addr] = [chr(data[20]), chr(data[19])]
                if all(v is not None for v in self.ps):
                    out_array = []
                    for i in self.ps:
                        out_array += i
                    text = "".join(out_array).strip()
                    if re.match("^[A-Za-z0-9 -]+$", text):
                        self.name = text
                        self.complete = True

            elif self.group == 2 and data[17] > 0:
                addr = block_b & 0x0F
                self.addrs.append(addr)
                self.rt[addr] = [chr(data[18]), chr(
                    data[17]), chr(data[20]), chr(data[19])]
                if all(v is not None for v in self.rt):
                    #self.complete = True
                    out_array = []
                    for i in self.rt:
                        out_array += i
                    self.radio_text = "".join(out_array).strip()
                    self.rt = [None]*16
                    self.addrs = []
                    self.fail_count = 0
                    print(self.radio_text)
                elif len(self.addrs) > 32:
                    max_val = max(self.addrs)
                    tmp_rt = self.rt[:max_val+1]
                    if all(v is not None for v in tmp_rt):
                        print('radiotext len {}'.format(max_val))
                        out_array = []
                        for i in tmp_rt:
                            out_array += i
                        self.radio_text = "".join(out_array).strip()
                        self.rt = [None]*16
                        self.addrs = []
                        self.fail_count = 0
                        print(self.radio_text)
                    else:
                        print('radiotext_fail {}'.format(max_val))
                        self.fail_count += 1
                        print(self.fail_count)
                        if self.fail_count > 5:
                            self.rt = [None]*16
                            self.addrs = []
                            self.fail_count = 0

