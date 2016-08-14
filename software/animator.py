import math
from colorsys import *

SIN_CHANGE_PER_TIME = 0.5
SIN_CHANGE_PER_PX   = 3.0
SIN_SIZE_PER_STRIP  = 20.0

class animator():

    def __init__(self, brightness):
        self.brightness = brightness

    def render(self, bulb):
        i = bulb.counter
        data = bytearray(bulb.strands * bulb.pixels * bulb.bpp)
        
        for y in range(0, bulb.strands):
            for x in range(0, bulb.pixels):
	            hue = math.sin((i*SIN_CHANGE_PER_TIME + x*SIN_CHANGE_PER_PX) / SIN_SIZE_PER_STRIP)
	            normalized_hue = (hue + 1.0) / 2 # Normalized to 0..1
	            r,g,b = hsv_to_rgb(normalized_hue, 1.0, 1.0)
	            r = int(r * 255)
	            g = int(g * 255)
	            b = int(b * 255)
                
	            data[(x+y)*bulb.bpp + 0] = self.brightness
	            data[(x+y)*bulb.bpp + 1] = b
	            data[(x+y)*bulb.bpp + 2] = g
	            data[(x+y)*bulb.bpp + 3] = r

        return data
