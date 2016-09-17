import socket
import time
import threading
from LedBulb import LedBulb
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol
from Config import Config

BULB_TIME_TO_LIVE = 20
ANIMATION_SPEED = 30.0 # in FPS
TIME_PER_FRAME = 1/ANIMATION_SPEED

def heartbeat(bulbs, ip, data):
    if ip in bulbs:
        bulbs[ip].ping()
    else:
        bulb = LedBulb(ip, data)
        bulbs[ip] = bulb
        print("Bulb #%d found: %s" % (len(bulbs), str(bulb)))


class HeartbeatReciever(DatagramProtocol):
    def __init__(self, bulbs):
        self.bulbs = bulbs

    def startProtocol(self):
        "Called when transport is connected"
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"

    def datagramReceived(self, data, source):
          ip, port = source
          heartbeat(self.bulbs, ip, data)


class animationThread(threading.Thread):
    def __init__(self, bulbs, animator):
        threading.Thread.__init__(self)
        self.animator = animator
        self.bulbs = bulbs

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
            if (time.time() - bulb.timestamp < BULB_TIME_TO_LIVE):
                self.process_a_bulb(bulb)

    def animate(self):
        timestamp = 0

        while True:
            new_time = time.time()
            time_to_wait = min(TIME_PER_FRAME, abs(timestamp + TIME_PER_FRAME - new_time))
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
        reactor.listenMulticast(self.config.receive_port, HeartbeatReciever(self.bulbs), listenMultiple=True)
        threading.Thread(target=reactor.run, args=(False,)).start()

        anim = animationThread(self.bulbs, self.animator)
        anim.start()
