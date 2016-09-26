class AbstractAnimation():

    def __init__(self, config):
        self.config = config

    def render(self, bulb):
        print("AbstractAnimation should never execute render()")
