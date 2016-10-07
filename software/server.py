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
        clients = ClientManager(config, console, animations, ledBulbs)
        update = UpdateServer(config)

        clients.run()

        try:
            update.run()
        except FileNotFoundError:
            # No update files found.
            pass

        console.start()

    except KeyboardInterrupt:
        os._exit(1)

    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        raise
