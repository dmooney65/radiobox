from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1309
from PIL import Image, ImageDraw


#PINS
#3	D0	Clock	P01-23	GPIO 11 (SCLK)
#4	D1	MOSI	P01-19	GPIO 10 (MOSI)
#5	RST	Reset	P01-16	GPIO 17 *** 3.3V!!!! for ssh1106
#6	DC	Data/Command	P01-18	GPIO 24
#7	CS	Chip Select	P01-26	GPIO 7 (CE1)
class Oled():
    _device = None
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Oled, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(self):
        serial = spi(port=0, device=1, gpio_RST=6, bus_speed_hz=4000000)
        # keep RST param and lowish bus speed
        #oled = sh1106(serial, rotate=2)
        self._device = ssd1309(serial)
        #self.oled.contrast(128)
        self._instance = 1

    def get_device(self):
        return self._device

class TextImage():
    def __init__(self, device, text, font):
        with canvas(device) as draw:
            w, h = draw.textsize(text, font)
        self.image = Image.new(device.mode, (w, h))
        draw = ImageDraw.Draw(self.image)
        draw.text((0, 0), text, font=font, fill="white")
        del draw
        self.width = w
        self.height = h

class Synchroniser():
    def __init__(self):
        self.synchronised = {}

    def busy(self, task):
        self.synchronised[id(task)] = False

    def ready(self, task):
        self.synchronised[id(task)] = True

    def is_synchronised(self):
        for task in self.synchronised.items():
            if task[1] is False:
                return False
        return True

class Scroller():
    WAIT_SCROLL = 1
    SCROLLING = 2
    WAIT_REWIND = 3
    WAIT_SYNC = 4

    def __init__(self, image_composition, rendered_image, scroll_delay, synchroniser):
        self.image_composition = image_composition
        self.speed = 1
        self.image_x_pos = 0
        self.rendered_image = rendered_image
        self.image_composition.add_image(rendered_image)
        self.max_pos = rendered_image.width - image_composition().width
        self.delay = scroll_delay
        self.ticks = 0
        self.state = self.WAIT_SCROLL
        self.synchroniser = synchroniser
        self.render()
        self.synchroniser.busy(self)
        self.cycles = 0
        self.must_scroll = self.max_pos > 0

    def __del__(self):
        self.image_composition.remove_image(self.rendered_image)

    def tick(self):

        # Repeats the following sequence:
        #  wait - scroll - wait - rewind -> sync with other scrollers -> wait
        if self.state == self.WAIT_SCROLL:
            if not self.is_waiting():
                self.cycles += 1
                self.state = self.SCROLLING
                self.synchroniser.busy(self)

        elif self.state == self.WAIT_REWIND:
            if not self.is_waiting():
                self.synchroniser.ready(self)
                self.state = self.WAIT_SYNC

        elif self.state == self.WAIT_SYNC:
            if self.synchroniser.is_synchronised():
                if self.must_scroll:
                    self.image_x_pos = 0
                    self.render()
                self.state = self.WAIT_SCROLL

        elif self.state == self.SCROLLING:
            if self.image_x_pos < self.max_pos:
                if self.must_scroll:
                    self.render()
                    self.image_x_pos += self.speed
            else:
                self.state = self.WAIT_REWIND

    def render(self):
        self.rendered_image.offset = (self.image_x_pos, 0)

    def is_waiting(self):
        self.ticks += 1
        if self.ticks > self.delay:
            self.ticks = 0
            return False
        return True

    def get_cycles(self):
        return self.cycles
