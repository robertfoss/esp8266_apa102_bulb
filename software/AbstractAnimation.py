class AbstractAnimation():

    def __init__(self, config):
        self.config = config

    def render(self, bulb):
        print("AbstractAnimation should never execute render()")

    def start(self):
        print("%s.start()" % self.__class__.__name__)

    def stop(self):
        print("%s.stop()" % self.__class__.__name__)
