import glob, os
import importlib
import Config
from animations.SyncdRainbow import SyncdRainbow
from animations.StaticRainbow import StaticRainbow

class AnimationManager():

    def __init__(self, config):
        self.config = config
        self.loadAnimations()

    def loadAnimations(self):
        self.animations = []
        path = Config.getPwd() + "/animations"
        os.chdir(path)
        for pyFile in glob.glob("*.py"):
            if pyFile == "AbstractAnimation.py":
                continue
            className = os.path.splitext(pyFile)[0]
            modulePath = ("animations.%s" % className)
            module = importlib.import_module(modulePath)
            animationClass = getattr(module, className)
            animation = animationClass(self.config)
            self.animations += [ animation ]

        self.currAnimation = 0
        self.numAnimations = len(self.animations)

    def animation(self):
        return self.animations[self.currAnimation]

    def render(self, bulbs):
        self.animation().render(bulbs)
