#!/usr/bin/env python3

import socket
import time
import sys
import os
import math
import time
import inspect
import hashlib
import threading
import threading
from colorsys import *
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.protocol import DatagramProtocol
from threading import Thread
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer



SEND_PORT = 10001
RECEIVE_PORT = 10000
HTTP_PORT = 10000
BULB_TIME_TO_LIVE = 20
ANIMATION_SPEED = 30.0 # in FPS
TIME_PER_FRAME = 1/ANIMATION_SPEED

PIXELS = 20
BPP = 4
BRIGHTNESS = 0x07

SIN_CHANGE_PER_TIME = 0.5
SIN_CHANGE_PER_PX   = 3.0
SIN_SIZE_PER_STRIP  = 20.0

bulbs = dict()

def render(buf, i):
    for x in range(0, PIXELS):
        hue = math.sin((i*SIN_CHANGE_PER_TIME + x*SIN_CHANGE_PER_PX) / SIN_SIZE_PER_STRIP)
        normalized_hue = (hue + 1.0) / 2 # Normalized to 0..1
        r,g,b = hsv_to_rgb(normalized_hue, 1.0, 1.0)
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)

        buf[x*BPP + 0] = BRIGHTNESS
        buf[x*BPP + 1] = b
        buf[x*BPP + 2] = g
        buf[x*BPP + 3] = r


def animate():
    timestamp = 0

    while True:
        new_time = time.time()
        time_to_wait = min(TIME_PER_FRAME, abs(timestamp + TIME_PER_FRAME - new_time))
        process_all_bulbs()
        time.sleep(time_to_wait)
        timestamp = new_time


def process_a_bulb(timestamp, counter, sock, ip):
#    print "Process bulb %s \t- %s \t- %s" % (str(ip), str(timestamp), str(counter))
    data = bytearray(PIXELS * BPP)
    render(data, counter)

    try:
        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.sendto(bytes(data[0:PIXELS * BPP]), (ip, SEND_PORT))
        sock.sendto(bytes(data[0:PIXELS * BPP]), (ip, SEND_PORT))
    except OSError:
        pass
    
    counter += 1
    bulbs[ip] = (timestamp, counter, sock)


def process_all_bulbs():
    for ip in list(bulbs.keys()):
        timestamp, counter, socket = bulbs[ip]
        if (time.time() - timestamp < BULB_TIME_TO_LIVE):
            process_a_bulb(timestamp, counter, socket, ip)
        else:
            print("Removing stale bulb %s" % (str(ip)))
            del bulbs[ip]


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


def get_pwd(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_pwd)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def sha256(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def doServeFile(self, filename):
    filepath = get_pwd() + "/" + filename
    if not (os.path.exists(filepath)):
        doInvalidQuery(self)
    
    with open(filepath) as f:
        self.output(f.read())

    print("%s was served: %s" % (self.client_address[0], filename))

def doServeHash(self, filename):
    filepath = get_pwd() + "/" + filename
    if not (os.path.exists(filepath)):
        doInvalidQuery(self)
    
    with open(filepath, encoding='utf-8') as f:
        hashString = sha256(filepath)
        self.output(hashString)
        print("%s was served hash of: %s - %s" % (self.client_address[0], filename, hashString))


def doServeIndex(self):
    
    for filename in os.listdir(get_pwd()):
        if filename.endswith(".lua"):
            self.output("%s %s\n" % (filename, sha256(get_pwd() + "/" + filename)))

def doInvalidQuery(self):
    self.send_response(404)
    self.end_headers()

class updateHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.split('/')
        if len(path) == 2 and path[1] == "index":
            doServeIndex(self)
        elif len(path) == 3 and path[1] == "hash" and path[2].endswith(".lua"):
            doServeHash(self, path[2])
        elif len(path) == 3 and path[1] == "file" and path[2].endswith(".lua"):
            doServeFile(self, path[2]) 
        else:
            doInvalidQuery(self)
        return

    def log_message(self, format, *args):
        return

    def output(self, string):
        self.wfile.write(bytes(string, "utf8"))

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class HTTPServer(threading.Thread):
    """Periodically updates the host db."""

    def run(self):
        print("Starting HTTP server...")
        server_address = ("127.0.0.1", HTTP_PORT)
        httpd = ThreadingSimpleServer(server_address, updateHTTPHandler)
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        http = HTTPServer()
        http.start()

        print("Starting up broadcast listener..")
        reactor.listenMulticast(RECEIVE_PORT, HeartbeatReciever(), listenMultiple=True)
        Thread(target=reactor.run, args=(False,)).start()

        while True:
            animate()

    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
