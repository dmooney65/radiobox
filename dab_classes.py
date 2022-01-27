import operator
import utils

class Status():
    def __init__(self, data):
        resp5 = utils.get_bitlist(data[6])
        self.acq = resp5[5]
        self.valid = resp5[7]
        self.rssi = data[7]
        self.snr = data[8]
        self.fic_quality = data[9]
        self.cnr = data[10]
        self.frequency = data[13] | data[14] << 8 | data[15] << 16 | data[16] << 24
        self.tuned_index = data[17]
        self.fft_offset = data[18]
        self.read_ant_cap = data[19] | data[20] << 8


class Ensemble():
    
    def __init__(self, data, status):
        self.eid = data[5] | data[6] << 8
        self.status = status
        self.ecc = data[23]
        self.charset = data[24]
        self.abbrev1 = data[25]
        self.abbrev0 = data[26]
        label = []
        if data[7] > 0:
            for l in range(7,7+16):
                if data[l] > 0:
                    label.append(chr(data[l]))
            self.label = "".join(label).strip()
        else: 
            self.label = None


class ServiceList():

    version = 0
    no_of_services = 0
    list_size = 0
    num_services = 0
    services = []    

    def __init__(self, data):
        self.success = True
        self.services = []
        self.version  = data[8] << 8 | data[7]
        self.list_size = data[6] << 8 | data[5]
        self.num_services = data[9]
        #Start pos after pad bytes 10, 11, 12
        pos = 13
        for dummy in range(self.num_services):
            service = Service()
            service.service_id = data[pos + 3] << 24 | data[pos + 2] << 16 | data[pos + 1] << 8 | data[pos]
            b_list = utils.get_bitlist(data[pos+4])
            service.prog_type = b_list[7]
            service.srv_link_flag = b_list[1]
            service.local_flag = data[pos + 5] & 0x80
            num_components = data[pos + 5] & 0x0F
            label = []
            if data[pos + 8] == 0:
                self.success = False
                break
            for l in range(pos+8,pos+8+16):
                if data[l] > 0:
                    label.append(chr(data[l]))

            service.num_components = num_components
            for dummy in range(num_components):
                service.components.append(data[pos + 25] << 8 | data[pos + 24])
                pos +=4

            service.service_label = "".join(label).strip()
            self.services.append(service)
            pos += 24
        self.services.sort(key=operator.attrgetter('service_label'))

class Service():

    def __init__(self):
        self.service_id = 0
        self.service_info = 0
        self.num_components = 0
        self.service_label = None
        self.components = []
        self.prog_type = 0
        self.srv_link_flag = 0
        self.local_flag = 0

class SubchanInfo():

    def __init__(self, data):
        self.service_mode = data[5]
        self.protection_info = data[6]
        self.subchan_bitrate = data[8] << 8 | data[7]
        self.num_cu = data[10] << 8 | data[9]
        self.cu_address = data[12] << 8 | data[11]

class AudioInfo():

    def __init__(self, data):
        self.bitrate = data[6] << 8 | data[5]
        self.samplerate = data[8] << 8 |  data[7]
        resp9 = utils.get_bitlist(data[9])
        self.audio_mode = resp9[6] << 1 | resp9[7]
        self.ps = resp9[4]
        self.sbr = resp9[5]
        self.drc_gain = data[10]
