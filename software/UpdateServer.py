import threading
import pyinotify
import os.path
import time
import asyncore
import re
import ntpath
import hashlib
import Config
from os.path import basename
from datetime import datetime,timedelta
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

FW_BIN_PATH = "/../firmware/bin"
FW_DEV_BIN_PATH = "/../firmware/.pioenvs"
binaries = dict()

def getMostRecentBin(dev_ok, version):
    rel_bin_file = None
    dev_bin_file = None
    rel_str = getBinString("rel", version)
    dev_str = getBinString("dev", version)

    try:
        rel_bin_file = binaries[rel_str]
    except KeyError:
        pass

    try:
        dev_bin_file = binaries[dev_str]
    except KeyError:
        pass

    if not dev_ok:
        return rel_bin_file

    if dev_bin_file == None:
        return rel_bin_file

    if rel_bin_file == None:
        return dev_bin_file
        
    if rel_bin_file.timestamp > dev_bin_file.timestamp:
        return rel_bin_file
    else:
        return dev_bin_file
    

def getBinString(binType, version):
    if binType == "dev":
        return "dev_hw_ver" + str(version)
    elif binType == "rel":
        return "rel_hw_ver" + str(version)

    if binType:
        return "dev_hw_ver" + str(version)
    else:
        return "rel_hw_ver" + str(version)

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
    fwBinPath = Config.getPwd() + FW_BIN_PATH
    fwDevBinPath = Config.getPwd() + FW_DEV_BIN_PATH

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
            self.timestamp = datetime.fromtimestamp(os.path.getmtime(path))
        else:
            self.timestamp = datetime.fromtimestamp(os.path.getctime(path))

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
    fwBinPath = Config.getPwd() + FW_BIN_PATH
    fwDevBinPath = Config.getPwd() + FW_DEV_BIN_PATH

    wm = pyinotify.WatchManager()
    eh = BinEventHandler()

    wd_rel = wm.add_watch(fwBinPath, events)
    wd_dev = wm.add_watch(fwDevBinPath, events, rec=True)

    notifier = pyinotify.ThreadedNotifier(wm, eh)
    notifier.start()

def calc_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def doServeFile(self, filename):
    filepath = Config.getPwd() + "/" + filename
    if not (os.path.exists(filepath)):
        doInvalidQuery(self)
    
    self.send_response(200)
    with open(filepath) as f:
        self.output(f.read())

    print("%s was served: %s" % (self.client_address[0], filename))

def doServeHash(self, filename):
    filepath = Config.getPwd() + "/" + filename
    if not (os.path.exists(filepath)):
        doInvalidQuery(self)
    
    self.send_response(200)
    with open(filepath, encoding='utf-8') as f:
        hashString = sha256(filepath)
        self.output(hashString)
        print("%s was served hash of: %s - %s" % (self.client_address[0], filename, hashString))


def doServeIndex(self):
    self.send_response(200)
    self.output(str(binaries))

def doServeUpdate(self):
    print("HTTP req headers: %s" % str(self.headers))

    version = self.headers.get('x-ESP8266-version')
    if not version:
        print("doServeUpdate() Version string not supplied")
        doInvalidQuery(self)
        return

    if "," not in version:
        print("doServeUpdate() Version string contains no \",\" divider: %s" % self.headers.get('x-ESP8266-version'))
        doInvalidQuery(self)
        return
    
    versions = version.split(",")
    if len(versions) < 3:
        print("doServeUpdate() Version string is too short: %s" % self.headers.get('x-ESP8266-version'))
        doInvalidQuery(self)
        return

    versions_dict = dict()
    for ver in versions:
        ver_split = ver.split("=")
        if len(ver_split) < 2:
            print("doServeUpdate() Invalid version substring: \"%s\"" % ver)
        
        versions_dict[ver_split[0]] = ver_split[1]

    print("versions_dict: \"%s\"" % str(versions_dict))
    hw_ver = int(versions_dict["hw"])
    fw_ver = int(versions_dict["fw"])
    ver_timestamp = versions_dict["timestamp"]

    ver_timestamp = datetime.strptime(ver_timestamp, '%a %b %d %H:%M:%S %Y')
    # Delay the timestamp of the to node to prevent update loops due to
    # the file modified time of a binary being newer than its own compilation
    # timestamp
    ver_timestamp += timedelta(seconds=30)

    bin_file = getMostRecentBin(True, hw_ver)
    if not bin_file:
        # No file found
        print("doServeUpdate() No binary for hw_ver %d found" % hw_ver)
        self.send_response(304)
        return

    print("bin_file.timestamp: %s" % str(bin_file.timestamp))
    print("ver_timestamp: %s" % str(ver_timestamp))
    if (bin_file.timestamp < ver_timestamp):
        print("doServeUpdate() Found old binary for hw_ver %d" % hw_ver)
        # Not modified
        self.send_response(304)
        return

    print("Sending update: type=%s hw_ver=%d timestamp=%s" % ("dev" if bin_file.isDev else "rel", hw_ver, str(bin_file.timestamp)))
    self.output(bin_file)


def doInvalidQuery(self):
    self.send_response(404)


class updateHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.content_length = 0
        self.content_type = "text/plain; charset=utf-8"

        print("HTTP req path: %s" % str(self.path))
        path = self.path.split('/')
        if self.path == "/":
            doServeIndex(self)
        if len(path) == 2 and path[1] == "index":
            doServeIndex(self)
        elif len(path) == 2 and path[1] == "update":
            doServeUpdate(self)
        elif len(path) == 3 and path[1] == "hash" and path[2].endswith(".lua"):
            doServeHash(self, path[2])
        elif len(path) == 3 and path[1] == "file" and path[2].endswith(".lua"):
            doServeFile(self, path[2]) 
        else:
            doInvalidQuery(self)

        self.send_header("Content-Type", self.content_type)
        self.send_header("Content-Length", self.content_length)
#        self.end_headers()
        return

    def log_message(self, format, *args):
        return

    def output(self, data):
        if isinstance(data, File):
            in_file = open(data.path, "rb") # opening for [r]eading as [b]inary
            byte_arr = in_file.read()
            in_file.close()
            self.content_length += len(byte_arr)
            filename = basename(data.path)
            self.send_response(200)
            self.send_header("Content-Disposition", "attachment; filename=%s" % filename)
            self.send_header("x-MD5", data.md5)
            self.content_type = "application/octet-stream"
            self.send_header("Content-Type", self.content_type)
            self.send_header("Content-Length", self.content_length)
            self.end_headers()
            self.wfile.write(byte_arr)
            return

        # Assume data is a string
        byte_arr = bytes(data, "utf8")
        self.content_length += len(byte_arr)
        self.wfile.write(byte_arr)
        return

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class HTTPServer(threading.Thread):
    """Periodically updates the host db."""

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        server_address = ("0.0.0.0", self.port)
        httpd = ThreadingSimpleServer(server_address, updateHTTPHandler)
        httpd.serve_forever()

class UpdateServer:
    def __init__(self, config):
        self.config = config

    def run(self):
        http = HTTPServer(self.config.http_port)
        http.start()
        scanBinDirs()
        setupINotify()

