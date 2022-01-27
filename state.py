
class State:

    def __init__(self, value=0, status=None, playing=None, timer=None, pause_timer=False):
        self.value = value
        self.status = status
        self.playing = playing
        self.timer = timer
        self.pause_timer = pause_timer

    def __str__(self):
        return self

    def set_value(self, val):
        self.value = val

    def set_pause_timer(self, paused):
        self.pause_timer = paused
