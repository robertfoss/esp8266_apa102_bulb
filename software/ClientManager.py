import socket
import time
import threading
from ledBulb import ledBulb
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol
from config import config

BULB_TIME_TO_LIVE = 20
ANIMATION_SPEED = 30.0 # in FPS
TIME_PER_FRAME = 1/ANIMATION_SPEED

bulbs = dict()

def heartbeat(ip, data):
    if ip in bulbs:
        bulbs[ip].ping()
    else:
        bulb = ledBulb(ip, data)
        bulbs[ip] = bulb
        print("Bulb #%d found: %s" % (len(bulbs), str(bulb)))


class HeartbeatReciever(DatagramProtocol):
    def __init__(self):
        pass

    def startProtocol(self):
        "Called when transport is connected"
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"

    def datagramReceived(self, data, source):
          ip, port = source
          heartbeat(ip, data)


class animationThread(threading.Thread):
    def __init__(self, animator):
        threading.Thread.__init__(self)
        self.animator = animator

    def process_a_bulb(self, bulb):
        data = self.animator.render(bulb)
        bulb.counter += 1
        try:
            bulb.socket.sendto(bytes(data), (bulb.ip, bulb.port))
        except OSError:
            pass

    def process_all_bulbs(self):
        for ip in list(bulbs.keys()):
            bulb = bulbs[ip]
            if (time.time() - bulb.timestamp < BULB_TIME_TO_LIVE):
                self.process_a_bulb(bulb)
            else:
                print("Removing stale bulb: %s" % (str(bulb.ip)))
                del bulbs[ip]

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


def runClientManager(animator, config):
    print("Starting up broadcast listener on port %d" % config.receive_port)
    reactor.listenMulticast(config.receive_port, HeartbeatReciever(), listenMultiple=True)
    threading.Thread(target=reactor.run, args=(False,)).start()

    anim = animationThread(animator)
    anim.start()
