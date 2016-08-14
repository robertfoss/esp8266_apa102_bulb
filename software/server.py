#!/usr/bin/env python3

from clientManager import runClientManager
from updateServer import runUpdateServer
from animator import animator

HTTP_PORT = 10000
RECEIVE_PORT = 10000
TRANSMIT_PORT = 10001

BRIGHTNESS = 0x03

if __name__ == "__main__":
    try:
        animator = animator(BRIGHTNESS)
        runClientManager(animator, RECEIVE_PORT)
        runUpdateServer(HTTP_PORT)
    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
