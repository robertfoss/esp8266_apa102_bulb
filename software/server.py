#!/usr/bin/env python3

import sys
from ClientManager import ClientManager
from UpdateServer import UpdateServer
from animator import animator
from config import config
from console import console

HTTP_PORT = 10000
RECEIVE_PORT = 10000
TRANSMIT_PORT = 10001

BRIGHTNESS = 0x09

if __name__ == "__main__":

    config = config();

    try:
        animator = animator(config)

        clients = ClientManager(animator, config)
        clients.run()

        update = UpdateServer(config)
        update.run()

        console = console(config)
        console.start()
    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
