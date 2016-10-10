import struct
import socket
import time
import operator

class Mac(object):
    def __init__(self, bytestring=None):
        if bytestring is None:
            self.bytes =  b'\x00\x00\x00\x00\x00\x00'
        else:
            self.bytes = bytestring

    def __str__(self):
        string = ":".join("{:02x}".format(c) for c in self.bytes)
        return string


class LedBulb(object):
    def __init__(self, config, ip, buf):
        self.config = config
        self.bulbId = -1
        self.sortOrder = -1
        self.ip = ip
        self.timestamp = time.time()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.counter = 0
        self.marked = 0

        try:
            (hwVer, fwVer, port, pixels, strands, bpp, mac_bytes) = struct.unpack('=BHHHBB6s', buf)
            self.mac = Mac(mac_bytes)
            self.hwVer = hwVer
            self.fwVer = fwVer
            self.port = port
            self.pixels = pixels
            self.strands = strands
            self.bpp = bpp
        except struct.error:
            try:
                (hwVer, fwVer, port, pixels, strands, bpp, mac_bytes) = struct.unpack('=BHHHBB', buf)
                self.mac = Mac()
                self.hwVer = hwVer
                self.fwVer = fwVer
                self.port = port
                self.pixels = pixels
                self.strands = strands
                self.bpp = bpp
            except struct.error:
                self.mac = Mac()
                self.hwVer = 1
                self.fwVer = 0
                self.port = self.config.transmit_port
                self.pixels = 21
                self.strands = 1
                self.bpp = 4

        self.pixelBuffer = bytearray(self.strands * self.pixels * self.bpp)

    def send(self):
        if self.marked == 1:
            for i in range(0,self.strands * self.pixels):
                self.pixelBuffer[i * self.bpp + 0] = self.config.brightness
                self.pixelBuffer[i * self.bpp + 1] = 255
                self.pixelBuffer[i * self.bpp + 2] = 0
                self.pixelBuffer[i * self.bpp + 3] = 0
        elif self.marked == 2:
            for i in range(0,self.strands * self.pixels):
                self.pixelBuffer[i * self.bpp + 0] = self.config.brightness
                self.pixelBuffer[i * self.bpp + 1] = 0
                self.pixelBuffer[i * self.bpp + 2] = 0
                self.pixelBuffer[i * self.bpp + 3] = 255
        try:
            self.socket.sendto(bytes(self.pixelBuffer), (self.ip, self.port))
        except OSError:
            pass

    def ping(self):
        self.timestamp = time.time()

    def __str__(self):
        string = ""
        if self.marked == 1:
            string += " -X- "
        elif self.marked == 2:
            string += " -|- "
        else:
            string += " - - "

        string += "#%d" % (self.bulbId)

        status = ""
        if self.timestamp + self.config.bulb_timeouts > time.time():
            status = "UP"
        else:
            status = "DOWN"

        string += status.center(6)

        netAddr = ""
        if hasattr(self, 'ip'):
            netAddr += str(self.ip)
        else:
            netAddr += "0.0.0.0"

        if hasattr(self, 'port'):
            netAddr += ":" + str(self.port)
        else:
            netAddr += ":0"
        string += netAddr.ljust(18)
        string += "  "

        mac = ""
        if hasattr(self, 'mac'):
            mac += str(self.mac)
        else:
            mac += "00:00:00:00:00:00"
        string += mac

#        string += "  "
#        if hasattr(self, 'hwVer'):
#            string += "hw_version=" + str(self.hwVer)
#        else:
#            string += "hw_version=?"

#        string += " "
#        if hasattr(self, 'fwVer'):
#            string += "fw_version=" + str(self.fwVer)
#        else:
#            string += "fw_version=?"

#        string += " "
#        if hasattr(self, 'pixels'):
#            string += "pixels=" + str(self.pixels)
#        else:
#            string += "pixels=?"

#        string += " "
#        if hasattr(self, 'strands'):
#            string += "strands=" + str(self.strands)
#        else:
#            string += "strands=0"

#        string += " "
#        if hasattr(self, 'bpp'):
#            string += "bytes/pixel=" + str(self.bpp)
#        else:
#            string += "bytes/pixel=?"
#
        return string


class LedBulbs():
    def __init__(self):
        self.bulbs = dict()

    def addBulb(self, config, ip, buf):
        bulb = LedBulb(config, ip, buf)
        bulb.bulbId = len(self.bulbs) + 1
        bulb.sortOrder = len(self.bulbs) + 1
        self.bulbs[ip] = bulb

    def orderedBulbs(self):
        return sorted(self.bulbs.values(), key=operator.attrgetter('sortOrder'))
