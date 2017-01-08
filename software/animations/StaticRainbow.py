import math
from colorsys import *
from animations.AbstractAnimation import AbstractAnimation


SIN_CHANGE_PER_TIME = 0.5
SIN_CHANGE_PER_PX   = 3.0
SIN_SIZE_PER_STRIP  = 20.0

class StaticRainbow(AbstractAnimation):


    def __init__(self, config):
        super().__init__(config)

    def render(self, bulbs):
        for bulb in bulbs:
            self.renderBulb(bulb)

    def renderBulb(self, bulb):
        i = bulb.counter

        for y in range(0, bulb.strands):
            for x in range(0, bulb.pixels):
	            hue = math.sin((i*SIN_CHANGE_PER_TIME + x*SIN_CHANGE_PER_PX) / SIN_SIZE_PER_STRIP)
	            normalized_hue = (hue + 1.0) / 2 # Normalize to 0..1
	            r,g,b = hsv_to_rgb(normalized_hue, 1.0, 1.0)
	            r = int(r * 255)
	            g = int(g * 255)
	            b = int(b * 255)

	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 0] = self.config.brightness
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 1] = b
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 2] = g
	            bulb.pixelBuffer[(x+y*bulb.pixels)*bulb.bpp + 3] = r
