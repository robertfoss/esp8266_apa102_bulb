#!/usr/bin/env python3

import sys
from ClientManager import ClientManager
from UpdateServer import UpdateServer
from animator import animator
from Config import Config
from Console import Console

if __name__ == "__main__":

    config = Config();

    try:
        animator = animator(config)

        clients = ClientManager(animator, config)
        clients.run()

        update = UpdateServer(config)
        update.run()

        console = Console(config)
        console.start()
    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
