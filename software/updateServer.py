import threading
import pyinotify
import os.path
import time
import asyncore
import sys
import inspect
import re
import ntpath
import hashlib
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

FW_BIN_PATH = "/../firmware/bin"
FW_DEV_BIN_PATH = "/../firmware/.pioenvs"
binaries = dict()

def getBinString(binType, version):
    if binType == "dev":
        return "dev_v" + str(version)
    elif binType == "rel":
        return "rel_v" + str(version)

    if binType:
        return "dev_v" + str(version)
    else:
        return "rel_v" + str(version)

def getFileVersion(path):
    regexp = re.findall(r'_v(\d+)', path)
    if len(regexp) != 0:
        return int(regexp[-1])
    return 0;

def getFileReleaseType(path):
    pathArr = path.split('/')
    if pathArr[-3] == ".pioenvs":
        return "dev"
    if pathArr[-2] == "bin":
        return "rel"
    return None

def acceptFile(path):
    if not path.endswith(".bin"):
        return False
    if getFileVersion(path) == 0:
        return False
    if getFileReleaseType == None:
        return False
    return True

def processFile(path):
    if acceptFile(path):
        binary = File(path)
        binaries[str(binary)] = binary
        print("Firmware binary found: %s  -- %s" % (str(binary), binary.path))

def getBinFile(isDev, version):
    if (version == 1 or version == 2):
        return binaries[getBinString(isDev, 1)]
    elif (version == 3 or version == 4):
        return binaries[getBinString(isDev, 4)]
    return None

def scanBinDirs():
    fwBinPath = get_pwd() + FW_BIN_PATH
    fwDevBinPath = get_pwd() + FW_DEV_BIN_PATH

    for file in os.listdir(fwBinPath):
        processFile(fwBinPath + os.sep + file)

    for file in os.listdir(fwDevBinPath):
        filename = ntpath.basename(os.path.abspath(file))
        if filename.startswith("esp8266_apa102_v"):
            for file2 in os.listdir(fwDevBinPath + os.sep + filename):
                processFile(fwDevBinPath + os.sep + filename + os.sep + file2)

class File():
    def __init__(self, path):
        self.path = path
        self.md5 = calc_md5(path)
        self.version = getFileVersion(path)
        
        if (os.path.getmtime(path) > os.path.getctime(path)):
            self.timestamp = os.path.getmtime(path)
        else:
            self.timestamp = os.path.getctime(path)

        if getFileReleaseType(path) == "dev":
            self.isDev = True
        else:
            self.isDev = False

    def __str__(self):
        return getBinString(self.isDev, self.version)

class BinEventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        processFile(event.pathname)

    def process_IN_MODIFY(self, event):
        processFile(event.pathname)

    def process_IN_DELETE(self, event):
        if acceptFile(event.pathname):
            isDev = getFileReleaseType(event.pathname)
            version = getFileVersion(event.pathname)
            fileStr = getBinString(isDev, version)
            print("Firmware binary removed: %s  -- %s" % (str(binaries[fileStr]), binaries[fileStr].path))
            del binaries[fileStr]

    def process_IN_ATTRIB(self, event):
        processFile(event.pathname)


def setupINotify():
    events = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_ATTRIB
    fwBinPath = get_pwd() + FW_BIN_PATH
    fwDevBinPath = get_pwd() + FW_DEV_BIN_PATH

    wm = pyinotify.WatchManager()
    eh = BinEventHandler()

    wd_rel = wm.add_watch(fwBinPath, events)
    wd_dev = wm.add_watch(fwDevBinPath, events, rec=True)

    notifier = pyinotify.ThreadedNotifier(wm, eh)
    notifier.start()


def get_pwd(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_pwd)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def calc_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

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
            self.output("%s %s\n" % (filename, md5(get_pwd() + os.sep + filename)))

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

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        print("Starting HTTP server...")
        server_address = ("127.0.0.1", self.port)
        httpd = ThreadingSimpleServer(server_address, updateHTTPHandler)
        httpd.serve_forever()

def runUpdateServer(port):
    http = HTTPServer(port)
    http.start()
    scanBinDirs()
    setupINotify()

