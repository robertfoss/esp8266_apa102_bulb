SIN_CHANGE_PER_TIME = 0.5
SIN_CHANGE_PER_PX   = 3.0
SIN_SIZE_PER_STRIP  = 20.0

class AbstractAnimation(object):

    def __init__(self, config):
        self.config = config

    def render(self, bulb):
        print("AbstractAnimation should never execute render()")
