import struct
import time
import socket

class LedBulb(object):
    def __init__(self, config, bulb_id, ip, buf):
        self.config = config
        self.bulb_id = bulb_id
        self.ip = ip
        self.timestamp = time.time()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.counter = 0

        try:
            (hwVer, fwVer, port, pixels, strands, bpp) = struct.unpack('=BHHHBB', buf)
            self.hwVer = hwVer
            self.fwVer = fwVer
            self.port = port
            self.pixels = pixels
            self.strands = strands
            self.bpp = bpp
        except struct.error:
            self.hwVer = 1
            self.fwVer = 0
            self.port = 10001
            self.pixels = 21
            self.strands = 1
            self.bpp = 4

    def ping(self):
        self.timestamp = time.time()

    def __str__(self):
        string = "#%d " % (self.bulb_id)

        if hasattr(self, 'ip'):
            string += str(self.ip)
        else:
            string += "0.0.0.0"

        if hasattr(self, 'port'):
            string += ":" + str(self.port)
        else:
            string += ":0"

        string += " - "

        if hasattr(self, 'hwVer'):
            string += "hw_version=" + str(self.hwVer)
        else:
            string += "hw_version=?"

        string += " "

        if hasattr(self, 'fwVer'):
            string += "fw_version=" + str(self.fwVer)
        else:
            string += "fw_version=?"

        string += " "

        if hasattr(self, 'pixels'):
            string += "pixels=" + str(self.pixels)
        else:
            string += "pixels=?"

        string += " "

        if hasattr(self, 'strands'):
            string += "strands=" + str(self.strands)
        else:
            string += "strands=0"

        string += " "

        if hasattr(self, 'bpp'):
            string += "bytes/pixel=" + str(self.bpp)
        else:
            string += "bytes/pixel=?"

        return string
