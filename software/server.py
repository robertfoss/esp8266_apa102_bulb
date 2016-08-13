#!/usr/bin/env python3

from clientManager import runClientManager
from updateServer import runUpdateServer
from animator import animator

HTTP_PORT = 10000
RECEIVE_PORT = 10000
TRANSMIT_PORT = 10001

PIXELS = 20
BITS_PER_PIXEL = 4
BRIGHTNESS = 0x07



if __name__ == "__main__":
    try:
        animator = animator(BRIGHTNESS, PIXELS, BITS_PER_PIXEL)
        runClientManager(animator, RECEIVE_PORT, TRANSMIT_PORT)
        runUpdateServer(HTTP_PORT)


    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
