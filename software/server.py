#!/usr/bin/env python3

import sys
from ClientManager import ClientManager
from UpdateServer import UpdateServer
from AnimationManager import AnimationManager
from Config import Config
from Console import Console
from LedBulb import LedBulbs

if __name__ == "__main__":

    config = Config();

    try:
        animations = AnimationManager(config)

        ledBulbs = LedBulbs()

        console = Console(config, ledBulbs, animations)
        console.start()

        clients = ClientManager(config, console, animations, ledBulbs)
        clients.run()

        update = UpdateServer(config)
        update.run()

    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
