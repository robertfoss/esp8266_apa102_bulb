import sys, inspect, os

class Config(object):
    def __init__(self):
        self.http_port = 10000
        self.receive_port = 10000
        self.transmit_port = 10001
        self.brightness = 0x09
        self.bulb_timeouts = 20
        self.animation_speed = 30.0 # in FPS
        self.time_per_frame = 1 / self.animation_speed


def getPwd(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(getPwd)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)
