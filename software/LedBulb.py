import struct
import time
import socket


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
    def __init__(self, config, bulb_id, ip, buf):
        self.config = config
        self.bulb_id = bulb_id
        self.ip = ip
        self.timestamp = time.time()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.counter = 0

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

    def ping(self):
        self.timestamp = time.time()

    def __str__(self):
        string = "#%d" % (self.bulb_id)

        status = ""
        if self.timestamp + self.config.bulb_timeouts > time.time():
            status = "UP"
        else:
            status = "DOWN"

        string += status.center(6)

        if hasattr(self, 'ip'):
            string += str(self.ip)
        else:
            string += "0.0.0.0"

        if hasattr(self, 'port'):
            string += ":" + str(self.port)
        else:
            string += ":0"

        string += "  "

        if hasattr(self, 'mac'):
            string += str(self.mac)
        else:
            string += "00:00:00:00:00:00"

        string += "  "

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


class LedBulbs():
    def __init__(self):
        self.bulbs = dict()
