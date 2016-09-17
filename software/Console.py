from blessed import Terminal
import threading
import operator

import ClientManager
import Config

class Console(threading.Thread):
    def __init__(self, config, clients):
        threading.Thread.__init__(self)
        self.config = config
        self.clients = clients
        self.bulbs = clients.bulbs
        self.t = Terminal()
        self.top_line = 0

    def resetScreen(self):
        self.top_line = 0

    def renderScreen(self):
        for bulb in (sorted(self.bulbs.values(), key=operator.attrgetter('bulb_id'))):
            self.printTop(str(bulb))o       

    def updateTerminal(self):
        with self.t.cbreak():
            val = self.t.inkey()
            if val.name == 'KEY_UP':
                self.brightnessUp()
            elif val.name == 'KEY_DOWN':
                self.brightnessDown()
        self.renderScreen()
        
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

    def printTop(self, str):
        with self.t.location(0, self.top_line):
            self.top_line += 1
            print(str)

    def printBottom(self, str):
        with self.t.location(0, self.t.height - 1):
            print(str)
