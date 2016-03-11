from random import *
from os import listdir
from os.path import isfile, join

class generator():
    NO_TARGETS_WIDE = 6
    NO_TARGETS_TALL = 6
    NO_TARGETS_DEEP = 12
    TARGET_COUNT_LONG_SURFACE = 8
    TARGET_COUNT_SQUARE_SURFACE = 4
    KEY_X = 2
    KEY_Y = 2
    x = 0
    y = 0
    icon = 0
    usedLocs = []
    usedIcons = []
    numberOfImages = 0
    availableImages = []

    def getXYandIcon(self, wallType):
        xWidth = 0
        yWidth = 0
        if wallType == "square":
            xWidth = self.NO_TARGETS_WIDE
            yWidth = self.NO_TARGETS_TALL
        elif wallType == "long":
            xWidth = self.NO_TARGETS_DEEP
            yWidth = self.NO_TARGETS_TALL
        elif wallType == "longFlip":
            xWidth = self.NO_TARGETS_WIDE
            yWidth = self.NO_TARGETS_DEEP
        xPick = randint(1, xWidth)
        yPick = randint(1, yWidth)
        while (xPick, yPick) in self.usedLocs:
            xPick = randint(1, xWidth)
            yPick = randint(1, yWidth)
        self.x = xPick
        self.y = yPick
        self.usedLocs.append((self.x, self.y))
        iconPick = self.availableImages[randint(0, self.numberOfImages-1)]
        while iconPick in self.usedIcons:
            iconPick = self.availableImages[randint(0, self.numberOfImages-1)]
        self.icon = iconPick
        self.usedIcons.append(self.icon)

    def clearUsedLocs(self):
        self.checkForDuplicates(self.usedLocs)
        self.usedLocs = []

    def clearUsedIcons(self):
        self.checkForDuplicates(self.usedIcons)
        self.usedIcons = []

    def checkForDuplicates(self, list):
        seen = set()
        for x in list:
            if x in seen:
                print "ERROR: Duplicate found"
            seen.add(x)
        return False


    def buildFile(self):
        self.availableImages = [f for f in listdir("img/") if isfile(join("img/", f))]
        for x in range(0, len(self.availableImages)):
            self.availableImages[x] = self.availableImages[x].split(".")[0]
        self.numberOfImages = len(self.availableImages)
        fo = open("targets.ini", "wb")
        fo.write("[configuration]\n")
        fo.write("NO_TARGETS_WIDE=" + str(self.NO_TARGETS_WIDE) + "\n")
        fo.write("NO_TARGETS_TALL=" + str(self.NO_TARGETS_TALL) + "\n")
        fo.write("NO_TARGETS_DEEP=" + str(self.NO_TARGETS_DEEP) + "\n")
        fo.write("TARGET_COUNT_LONG_SURFACE=" + str(self.TARGET_COUNT_LONG_SURFACE) + "\n")
        fo.write("TARGET_COUNT_SQUARE_SURFACE=" + str(self.TARGET_COUNT_SQUARE_SURFACE) + "\n")
        fo.write("KEY_X=" + str(self.KEY_X) + "\n")
        fo.write("KEY_Y=" + str(self.KEY_Y) + "\n\n")
        for w in range(1,101):
            fo.write("[" + str(w) + "]\n")
            fo.write("wallF=")
            self.getXYandIcon("square")
            while self.x == self.KEY_X and self.y == self.KEY_Y:
                self.getXYandIcon("square")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                self.getXYandIcon("square")
                while self.x == self.KEY_X and self.y == self.KEY_Y:
                    self.getXYandIcon("square")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallB=")
            self.getXYandIcon("square")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                self.getXYandIcon("square")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallL=")
            self.getXYandIcon("long")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("long")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallR=")
            self.getXYandIcon("long")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("long")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("ceiling=")
            self.getXYandIcon("longFlip")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("longFlip")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            iconIndex = randint(0,len(self.usedIcons)-1)
            icon = self.usedIcons[iconIndex]
            fo.write("target=" + str(icon))
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()
        fo.close()

gen = generator()
gen.buildFile()