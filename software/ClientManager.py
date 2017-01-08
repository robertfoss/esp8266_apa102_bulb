import socket
import time
import threading
from LedBulb import LedBulb
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol
from Config import Config


class HeartbeatReciever(DatagramProtocol):
    def __init__(self, config, console, ledBulbs):
        self.config = config
        self.console = console
        self.ledBulbs = ledBulbs

    def startProtocol(self):
        "Called when transport is connected"
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"

    def datagramReceived(self, data, source):
          ip, port = source
          self.heartbeat(ip, data)

    def heartbeat(self, ip, data):
        if ip in self.ledBulbs.bulbs:
            self.ledBulbs.bulbs[ip].ping()
        else:
            self.ledBulbs.addBulb(self.config, ip, data)
            self.console.update()


class AnimationThread(threading.Thread):
    def __init__(self, config, ledBulbs, animationManager):
        threading.Thread.__init__(self)
        self.animations = animationManager
        self.ledBulbs = ledBulbs
        self.config = config

    def processAllBulbs(self):
        activeBulbs = []
        for bulb in self.ledBulbs.orderedBulbs():
            if (time.time() - bulb.timestamp < self.config.bulb_timeouts):
                bulb.counter += 1
                activeBulbs += [ bulb ]

        self.animations.render(activeBulbs)

        for bulb in activeBulbs:
            bulb.send()

    def animate(self):
        timestamp = 0

        while True:
            new_time = time.time()
            time_to_wait = min(self.config.time_per_frame, abs(timestamp + self.config.time_per_frame - new_time))
            self.processAllBulbs()
            time.sleep(time_to_wait)
            timestamp = new_time

    def run(self):
        while True:
            self.animate()

class ClientManager:
    def __init__(self, config, console, animationManager, ledBulbs):
        self.config = config
        self.console = console
        self.animations = animationManager
        self.ledBulbs = ledBulbs

    def run(self):
        reactor.listenMulticast(self.config.receive_port, HeartbeatReciever(self.config, self.console, self.ledBulbs), listenMultiple=True)
        threading.Thread(target=reactor.run, args=(False,)).start()

        anim = AnimationThread(self.config, self.ledBulbs, self.animations)
        anim.start()
