#from timer import InfiniteTimer

class State:
 
    #__shared_state = dict()

    #value = 0
    #status = None
    #playing = None
    #timer = None

    #@staticmethod
    #def getInstance():
    #    
    #    """Static Access Method"""
    #    if State.__shared_instance == 'GeeksforGeeks':
    #        State()
    #    return State.__shared_instance

    def __init__(self, value=0, status=None, playing=None, timer=None, pause_timer=False):
        #self.value = value
        #self.status = status
        #self.playing = playing
        #self.timer = timer
        #self.pause_timer = pause_timer
        #self.__dict__ = self.__shared_state
        self.value = 0
        self.status = None
        self.playing = None
        self.timer = None
        self.pause_timer = False

        #"""virtual private constructor"""
        #if State.__shared_instance != 'GeeksforGeeks':
        #    raise Exception ("This class is a singleton class !")
        #else:
        #    State.__shared_instance = self

    def __str__(self):
        return self

    def set_value(self, val):
        self.value = val

    def set_pause_timer(self, paused):
        self.pause_timer = paused

    #def create_timer(self, seconds, func):
    #    self.timer = InfiniteTimer(seconds, func)
    
    #def cancel_timer(self):
    #    self.timer.cancel()
    
    #def start_timer(self):
    #    self.timer.start()