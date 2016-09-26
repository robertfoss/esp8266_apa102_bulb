import glob, os
import importlib
from animations.SyncdRainbow import SyncdRainbow
from animations.StaticRainbow import StaticRainbow

class AnimationManager():

    def __init__(self, config):
        self.config = config
        self.loadAnimations(config)

    def loadAnimations(self, config):
        self.animations = []
        os.chdir("animations")
        for pyFile in glob.glob("*.py"):
            if pyFile == "AbstractAnimation.py":
                continue
            className = os.path.splitext(pyFile)[0]
            modulePath = ("animations.%s" % className)
            module = importlib.import_module(modulePath)
            animationClass = getattr(module, className)
            animation = animationClass(config)
            self.animations += [ animation ]

        self.currAnimation = 0
        self.numAnimations = len(self.animations)

    def animation(self):
        return self.animations[self.currAnimation]

    def render(self, bulbs):
        self.animation().render(bulbs)
