from blessed import Terminal
import threading
import signal
import time

import ClientManager
import Config
from LedBulb import LedBulb
from LedBulb import LedBulbs


SYMBOL_ARROW_LEFT = u'\u2190'
SYMBOL_ARROW_UP = u'\u2191'
SYMBOL_ARROW_RIGHT = u'\u2192'
SYMBOL_ARROW_DOWN = u'\u2193'
SYMBOL_ARROW_LEFT_RIGHT = u'\u2194'

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Console(threading.Thread):
    def __init__(self, config, ledBulbs, animationManager):
        threading.Thread.__init__(self)
        self.config = config
        self.ledBulbs = ledBulbs
        self.animations = animationManager
        self.updateLock = threading.Lock()

        self.t = Terminal()
        self.topLine = 0
        self.moveMode = False
        self.markedLine = 2

        def on_resize(*args):
            self.update()
        signal.signal(signal.SIGWINCH, on_resize)

        self.updateThread()


    def resetScreen(self):
        self.topLine = 2

    def renderScreen(self):
        with self.updateLock:
            self.resetScreen()
            with self.t.fullscreen():
                for bulb in self.ledBulbs.orderedBulbs():
                    self.printTop(str(bulb), bulb.marked != 0)
                self.printKeymap()
                self.printStatus()

    def update(self):
        self.renderScreen()

    @threaded
    def updateThread(self):
        while True:
            self.update()
            time.sleep(0.250);


    def updateTerminal(self):
        with self.t.cbreak():
            val = self.t.inkey()
            if val.name == 'KEY_UP':
                self.keyUp()
            elif val.name == 'KEY_DOWN':
                self.keyDown()
            elif val.name == 'KEY_RIGHT':
                self.animationNext()
            elif val.name == 'KEY_LEFT':
                self.animationPrev()
            elif val.name == 'KEY_ESCAPE':
                self.esc()
            elif val in (" "):
                self.moveMode()
            else:
                pass

    def esc(self):
        self.toggleMoveMode(0)
        self.renderScreen()

    def keyUp(self):
        if self.moveMode == 0:
            self.brightnessUp()
        else:
            self.markUp()

    def keyDown(self):
        if self.moveMode == 0:
            self.brightnessDown()
        else:
            self.markDown()
        
    def run(self):
        self.update()
        while True:
            self.updateTerminal()

    def markUp(self):
        bulbs = self.ledBulbs.orderedBulbs()
        bulb1 = bulbs[self.markedLine - 2]
        if bulb1.marked == 2:
            bulb2 = None
            for bulb in bulbs:
                if bulb.marked == 1:
                    bulb2 = bulb
            for bulb in bulbs:
                bulb.marked = 0

            if bulb2 != None:
                bulb2.marked = 1
            else:
                bulb1.marked = 1
        else:
            for bulb in bulbs:
                bulb.marked = 0
        self.markedLine -= 1
        if self.markedLine < 2:
            self.markedLine = 2
        bulbs[self.markedLine - 2].marked = self.moveMode
        self.renderScreen()

    def markDown(self):
        bulbs = self.ledBulbs.orderedBulbs()
        bulb1 = bulbs[self.markedLine - 2]
        if bulb1.marked == 2:
            bulb2 = None
            for bulb in bulbs:
                if bulb.marked == 1:
                    bulb2 = bulb
            for bulb in bulbs:
                bulb.marked = 0

            if bulb2 != None:
                bulb2.marked = 1
            else:
                bulb1.marked = 1
        else:
            for bulb in bulbs:
                bulb.marked = 0
        self.markedLine += 1
        if self.markedLine > self.topLine - 1:
            self.markedLine = self.topLine - 1
        bulbs[self.markedLine - 2].marked = self.moveMode
        self.renderScreen()

    def brightnessUp(self):
        if (self.config.brightness + 1 > 31):
            self.config.brightness = 31
        else:
            self.config.brightness += 1
            self.renderScreen()

    def brightnessDown(self):
        if (self.config.brightness - 1 < 1):
            self.config.brightness = 1
        else:
            self.config.brightness -= 1
            self.renderScreen()

    def animationNext(self):
        idx = self.animations.currAnimation
        idx = (idx + 1) % self.animations.numAnimations
        self.animations.currAnimation = idx
        self.renderScreen()

    def animationPrev(self):
        idx = self.animations.currAnimation
        idx = (idx - 1) % self.animations.numAnimations
        self.animations.currAnimation = idx
        self.renderScreen()

    def moveMode(self, targetMode=None):
        if targetMode != None:
            self.moveMode = targetMode
        else:
            self.moveMode = (self.moveMode + 1) % 3

        if self.moveMode == 0:
            for bulb in self.ledBulbs.bulbs.values():
                bulb.marked = self.moveMode
        elif self.moveMode == 1:
            self.ledBulbs.orderedBulbs()[self.markedLine - 2].marked = self.moveMode
        elif self.moveMode == 2:
            self.ledBulbs.orderedBulbs()[self.markedLine - 2].marked = self.moveMode
        self.renderScreen()

    def printTop(self, str, revLine=False):
        with self.t.location(0, self.topLine):
            if revLine:
                print(self.t.reverse(str))
            else:
                print(str)
            self.topLine += 1

    def printBottom(self, str):
        with self.t.location(0, self.t.height - 2):
            print(str)

    def printKeymap(self):
        with self.t.location(0, self.t.height - 1):
            pass

    def printStatus(self):
        with self.t.location(0, self.t.height - 1):
            status = u"Brightness: {0}{1} ".format(SYMBOL_ARROW_UP, SYMBOL_ARROW_DOWN)
            status += (self.t.bold + "%s  " + self.t.normal)  % (str(self.config.brightness).ljust(2))
            status += u"Animation: {0} ".format(SYMBOL_ARROW_LEFT_RIGHT)
            animName = self.animations.animation().__class__.__name__
            status += (self.t.bold + "%s   " + self.t.normal)  % (animName.ljust(4))
            print(status)

        with self.t.location(0, self.t.height):
            status = ""
            status += ("HTTP port: " + self.t.bold + "%s   " + self.t.normal)  % (str(self.config.http_port).ljust(4))
            status += ("Receive port: " + self.t.bold + "%s   " + self.t.normal)  % (str(self.config.receive_port).ljust(4))
            print(status)

