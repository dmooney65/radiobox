import subprocess
import signal

CHANNELS = '2'
RATE = '48000'
FORMAT = 'S24_LE'
REC_DEVICE = 'hw:0,1'
PLAY_DEVICE = 'hw:0,0'


class Pipe():
    _instance = None
    _arecord_process = None
    _aplay_process = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Pipe, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(self):
        self._instance = 1
        
    def __del__(self):
        if self._arecord_process is not None:
            self._arecord_process.send_signal(signal.SIGINT)
            self._aplay_process.send_signal(signal.SIGINT)
            self._arecord_process = None
            self._aplay_process = None
        self._instance = None
    
    def start(self):
        if self._arecord_process is None:
            self._arecord_process = subprocess.Popen(["arecord", "-N", "-M", "-t", "raw", "-f",
                                                       FORMAT, "-r", RATE, "-c", CHANNELS, "-D", REC_DEVICE], stdout=subprocess.PIPE)
            self._aplay_process = subprocess.Popen(["aplay", "-f", FORMAT, "-r", RATE, "-c",
                                                     CHANNELS, "-D", PLAY_DEVICE], stdin=self._arecord_process.stdout, stdout=subprocess.PIPE)
    
    def stop(self):
        self.__del__()
    
    def is_playing(self):
        return self._instance == 1
        
