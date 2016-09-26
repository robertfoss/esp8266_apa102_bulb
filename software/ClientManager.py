import socket
import time
import threading
from LedBulb import LedBulb
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol
from Config import Config


class HeartbeatReciever(DatagramProtocol):
    def __init__(self, config, console, bulbs):
        self.config = config
        self.console = console
        self.bulbs = bulbs

    def startProtocol(self):
        "Called when transport is connected"
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"

    def datagramReceived(self, data, source):
          ip, port = source
          self.heartbeat(ip, data)

    def heartbeat(self, ip, data):
        if ip in self.bulbs:
            self.bulbs[ip].ping()
        else:
            bulb = LedBulb(self.config, len(self.bulbs) + 1, ip, data)
            self.bulbs[ip] = bulb
            self.console.update()


class animationThread(threading.Thread):
    def __init__(self, config, bulbs, animationManager):
        threading.Thread.__init__(self)
        self.animations = animationManager
        self.bulbs = bulbs

        self.config = config

    def processAllBulbs(self):
        activeBulbs = list()
        for ip in self.bulbs.values():
            bulb = self.bulbs[ip]
            if (time.time() - bulb.timestamp < self.config.bulb_timeouts):
                bulb.counter += 1
                activeBulbs += bulb

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
        self.bulbs = ledBulbs.bulbs

    def run(self):
        reactor.listenMulticast(self.config.receive_port, HeartbeatReciever(self.config, self.console, self.bulbs), listenMultiple=True)
        threading.Thread(target=reactor.run, args=(False,)).start()

        anim = animationThread(self.config, self.bulbs, self.animations)
        anim.start()


