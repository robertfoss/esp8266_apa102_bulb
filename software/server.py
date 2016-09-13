#!/usr/bin/env python3

import sys
from clientManager import runClientManager
from updateServer import runUpdateServer
from animator import animator
from config import config

HTTP_PORT = 10000
RECEIVE_PORT = 10000
TRANSMIT_PORT = 10001

BRIGHTNESS = 0x09

if __name__ == "__main__":

    cfg = config();

    try:
        animator = animator(cfg)
        runClientManager(animator, cfg)
        runUpdateServer(cfg)
    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
