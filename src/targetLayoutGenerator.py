from random import *

class generator():
    NO_TARGETS_WIDE = 6
    NO_TARGETS_TALL = 6
    NO_TARGETS_DEEP = 12
    TARGET_COUNT_LONG_SURFACE = 8
    TARGET_COUNT_SQUARE_SURFACE = 4
    x = 0
    y = 0
    icon = 0
    usedLocs = []
    usedIcons = []

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
        iconPick = randint(7, 144)
        while iconPick in self.usedIcons:
            iconPick = randint(7, 144)
        self.icon = iconPick
        self.usedIcons.append(self.icon)

    def clearUsedLocs(self):
        self.usedLocs = []

    def clearUsedIcons(self):
        self.usedIcons = []

    def buildFile(self):
        fo = open("targets.ini", "wb")
        fo.write("[configuration]\n")
        fo.write("NO_TARGETS_WIDE=" + str(self.NO_TARGETS_WIDE) + "\n")
        fo.write("NO_TARGETS_TALL=" + str(self.NO_TARGETS_TALL) + "\n")
        fo.write("NO_TARGETS_DEEP=" + str(self.NO_TARGETS_DEEP) + "\n")
        fo.write("TARGET_COUNT_LONG_SURFACE=" + str(self.TARGET_COUNT_LONG_SURFACE) + "\n")
        fo.write("TARGET_COUNT_SQUARE_SURFACE=" + str(self.TARGET_COUNT_SQUARE_SURFACE) + "\n\n")
        for w in range(1,101):
            fo.write("[" + str(w) + "]\n")
            fo.write("wallF=")
            self.getXYandIcon("square")
            fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                self.getXYandIcon("square")
                fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallB=")
            self.getXYandIcon("square")
            fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                self.getXYandIcon("square")
                fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallL=")
            self.getXYandIcon("long")
            fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("long")
                fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallR=")
            self.getXYandIcon("long")
            fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("long")
                fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("ceiling=")
            self.getXYandIcon("longFlip")
            fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("longFlip")
                fo.write(str(self.x) + "," + str(self.y) + ":" + str(self.icon))
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()
        fo.close()

gen = generator()
gen.buildFile()