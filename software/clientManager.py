import socket
import time
import threading
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol

BULB_TIME_TO_LIVE = 20
ANIMATION_SPEED = 30.0 # in FPS
TIME_PER_FRAME = 1/ANIMATION_SPEED

bulbs = dict()

def heartbeat(ip):
    timestamp = time.time()
    if ip in bulbs:
        _, counter, socket = bulbs[ip]
        bulbs[ip] = (timestamp, counter, socket)
    else:
        bulbs[ip] = (timestamp, 0, None)
        print("New bulb found - %s for a total of\t%d" % (str(ip), len(bulbs)))


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
          heartbeat(ip)


class animationThread(threading.Thread):
    def __init__(self, animator, transmitPort):
        threading.Thread.__init__(self)
        self.animator = animator
        self.transmitPort = transmitPort

    def process_a_bulb(self, timestamp, counter, sock, ip):
        data = self.animator.render(counter)

        try:
            if sock == None:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
                sock.sendto(bytes(data), (ip, self.transmitPort))
            sock.sendto(bytes(data), (ip, self.transmitPort))
        except OSError:
            pass
        
        counter += 1
        bulbs[ip] = (timestamp, counter, sock)


    def process_all_bulbs(self):
        for ip in list(bulbs.keys()):
            timestamp, counter, socket = bulbs[ip]
            if (time.time() - timestamp < BULB_TIME_TO_LIVE):
                self.process_a_bulb(timestamp, counter, socket, ip)
            else:
                print("Removing stale bulb %s" % (str(ip)))
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


def runClientManager(animator, receivePort, transmitPort):
    print("Starting up broadcast listener..")
    reactor.listenMulticast(receivePort, HeartbeatReciever(), listenMultiple=True)
    threading.Thread(target=reactor.run, args=(False,)).start()

    anim = animationThread(animator, transmitPort)
    anim.start()
