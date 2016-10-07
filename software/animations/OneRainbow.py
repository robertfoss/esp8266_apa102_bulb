import math
from colorsys import *
from AbstractAnimation import AbstractAnimation


SIN_CHANGE_PER_TIME = 0.125
SIN_CHANGE_PER_PX   = 3.0
SIN_SIZE_PER_STRIP  = 20.0

class OneRainbow(AbstractAnimation):

    def __init__(self, config):
        super().__init__(config)
        self.i = 0

    def render(self, bulbs):
        self.i += 1
        numBulbs = len(bulbs)
        if (numBulbs != 0):
            bulbPi = math.pi / numBulbs
        else:
            bulbPi = 0

        for bulb in bulbs:
            hue = math.sin((self.i * SIN_CHANGE_PER_TIME + bulb.bulbId * bulbPi) / SIN_SIZE_PER_STRIP)
            normalized_hue = (hue + 1.0) / 2 # Normalize to 0..1
            self.renderBulb(bulb, normalized_hue)

    def renderBulb(self, bulb, hue):
        for y in range(0, bulb.strands):
            for x in range(0, bulb.pixels):
	            r,g,b = hsv_to_rgb(hue, 1.0, 1.0)
	            r = int(r * 255)
	            g = int(g * 255)
	            b = int(b * 255)
                
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 0] = self.config.brightness
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 1] = b
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 2] = g
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 3] = r
