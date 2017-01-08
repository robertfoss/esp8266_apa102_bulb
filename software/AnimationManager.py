import glob, os
import importlib
import Config

class AnimationManager():

    def __init__(self, config):
        self.config = config
        self.activeIdx = 0
        self.loadAnimations()
        self.anim = self.animations[self.activeIdx]
        self.anim.start()

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

        self.numAnims = len(self.animations)

    def animation(self):
        return self.anim

    def startAnim(self):
        self.anim.start()

    def stopAnim(self):
        self.anim.stop()

    def switchAnim(self, idx):
        oldAnim = self.anim
        nextIdx = idx % self.numAnims
        nextAnim = self.animations[nextIdx]
        nextAnim.start()
        self.activeIdx = nextIdx
        self.anim = nextAnim
        oldAnim.stop()

    def render(self, bulbs):
        self.anim.render(bulbs)

    def next(self):
        idx = (self.activeIdx + 1) % self.numAnims
        self.switchAnim(idx)

    def prev(self):
        idx = (self.activeIdx - 1) % self.numAnims
        self.switchAnim(idx)
