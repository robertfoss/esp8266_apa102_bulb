import threading
import config
from blessed import Terminal

class console(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config
        self.t = Terminal()

    def updateTerminal(self):
        with self.t.cbreak():
            val = self.t.inkey()
            if val.name == 'KEY_UP':
                self.brightnessUp()
            elif val.name == 'KEY_DOWN':
                self.brightnessDown()
        
    def run(self):
        while True:
            self.updateTerminal()

    def brightnessUp(self):
        if (self.config.brightness + 1 > 31):
            self.config.brightness = 31
        else:
            self.config.brightness += 1
        self.printBottom("Brightness: %d" % self.config.brightness)


    def brightnessDown(self):
        if (self.config.brightness - 1 < 1):
            self.config.brightness = 1
        else:
            self.config.brightness -= 1
        self.printBottom("Brightness: %d" % self.config.brightness)

    def printBottom(self, str):
        with self.t.location(0, self.t.height - 1):
            print(str)
