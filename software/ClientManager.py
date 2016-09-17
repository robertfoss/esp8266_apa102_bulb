import socket
import time
import threading
from LedBulb import LedBulb
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol
from Config import Config


class HeartbeatReciever(DatagramProtocol):
    def __init__(self, config, bulbs):
        self.config = config
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
            print("Bulb #%d found: %s" % (len(self.bulbs), str(bulb)))


class animationThread(threading.Thread):
    def __init__(self, config, bulbs, animator):
        threading.Thread.__init__(self)
        self.animator = animator
        self.bulbs = bulbs
        self.config = config

    def process_a_bulb(self, bulb):
        data = self.animator.render(bulb)
        bulb.counter += 1
        try:
            bulb.socket.sendto(bytes(data), (bulb.ip, bulb.port))
        except OSError:
            pass

    def process_all_bulbs(self):
        for ip in list(self.bulbs.keys()):
            bulb = self.bulbs[ip]
            if (time.time() - bulb.timestamp < self.config.bulb_timeouts):
                self.process_a_bulb(bulb)

    def animate(self):
        timestamp = 0

        while True:
            new_time = time.time()
            time_to_wait = min(self.config.time_per_frame, abs(timestamp + self.config.time_per_frame - new_time))
            self.process_all_bulbs()
            time.sleep(time_to_wait)
            timestamp = new_time

    def run(self):
        while True:
            self.animate()

class ClientManager:
    def __init__(self, animator, config):
        self.animator = animator
        self.config = config
        self.bulbs = dict()

    def run(self):
        print("Starting up broadcast listener on port %d" % self.config.receive_port)
        reactor.listenMulticast(self.config.receive_port, HeartbeatReciever(self.config, self.bulbs), listenMultiple=True)
        threading.Thread(target=reactor.run, args=(False,)).start()

        anim = animationThread(self.config, self.bulbs, self.animator)
        anim.start()


