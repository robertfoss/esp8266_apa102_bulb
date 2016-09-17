from blessed import Terminal
import threading
import operator
import signal

import ClientManager
import Config

class Console(threading.Thread):
    def __init__(self, config, ledBulbs):
        threading.Thread.__init__(self)
        self.config = config
        self.bulbs = ledBulbs.bulbs

        self.t = Terminal()
        self.top_line = 1

        def on_resize(*args):
            self.update()

        signal.signal(signal.SIGWINCH, on_resize)

    def resetScreen(self):
        self.top_line = 1

    def renderScreen(self):
        self.resetScreen()
        with self.t.fullscreen():
            for bulb in (sorted(self.bulbs.values(), key=operator.attrgetter('bulb_id'))):
                self.printTop(str(bulb))
            self.printStatus()

    def update(self):
        self.renderScreen()

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

    def brightnessDown(self):
        if (self.config.brightness - 1 < 1):
            self.config.brightness = 1
        else:
            self.config.brightness -= 1

    def printTop(self, str):
        with self.t.location(0, self.top_line):
            self.top_line += 1
            print(str)

    def printBottom(self, str):
        with self.t.location(0, self.t.height - 1):
            print(str)

    def printStatus(self):
        with self.t.location(0, self.t.height):
            status = ""
            status += ("Brightness: " + self.t.bold + "%s  " + self.t.normal)  % (str(self.config.brightness).ljust(2))
            status += ("HTTP port: " + self.t.bold + "%s  " + self.t.normal)  % (str(self.config.http_port).ljust(4))
            status += ("Receive port: " + self.t.bold + "%s  " + self.t.normal)  % (str(self.config.receive_port).ljust(4))
            print(status)

