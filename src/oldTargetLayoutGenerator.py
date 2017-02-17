from random import *
from os import listdir
from os.path import isfile, join

class generator():
    CEILING_WIDE = 6
    CEILING_TALL = 10

    FRONT_WIDE = 6
    FRONT_TALL = 6

    BACK_WIDE = 6
    BACK_TALL = 6

    LEFT_WIDE = 10
    LEFT_TALL = 6

    RIGHT_WIDE = 10
    RIGHT_TALL = 4

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

    def getXYandIcon(self, wall):
        xWidth = 0
        yWidth = 0
        if wall == "front":
            xWidth = self.FRONT_WIDE
            yWidth = self.FRONT_TALL
        elif wall == "back":
            xWidth = self.BACK_WIDE
            yWidth = self.BACK_TALL
        elif wall == "left":
            xWidth = self.LEFT_WIDE
            yWidth = self.LEFT_TALL
        elif wall == "right":
            xWidth = self.RIGHT_WIDE
            yWidth = self.RIGHT_TALL
        elif wall == "ceiling":
            xWidth = self.CEILING_WIDE
            yWidth = self.CEILING_TALL
        xPick = randint(2, xWidth-1)
        yPick = randint(2, yWidth-1)
        while (xPick, yPick) in self.usedLocs:
            xPick = randint(2, xWidth-1)
            yPick = randint(2, yWidth-1)
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
            self.availableImages[x] = self.availableImages[x]
        self.numberOfImages = len(self.availableImages)
        fo = open("targets_OLD.ini", "wb")
        fo.write("[configuration]\n")
        fo.write("CEILING_WIDE=" + str(self.CEILING_WIDE) + "\n")
        fo.write("CEILING_TALL=" + str(self.CEILING_TALL) + "\n")
        fo.write("FRONT_WIDE=" + str(self.FRONT_WIDE) + "\n")
        fo.write("FRONT_TALL=" + str(self.FRONT_TALL) + "\n")
        fo.write("BACK_WIDE=" + str(self.BACK_WIDE) + "\n")
        fo.write("BACK_TALL=" + str(self.BACK_TALL) + "\n")
        fo.write("LEFT_WIDE=" + str(self.LEFT_WIDE) + "\n")
        fo.write("LEFT_TALL=" + str(self.LEFT_TALL) + "\n")
        fo.write("RIGHT_WIDE=" + str(self.RIGHT_WIDE) + "\n")
        fo.write("RIGHT_TALL=" + str(self.RIGHT_TALL) + "\n")
        fo.write("TARGET_COUNT_LONG_SURFACE=" + str(self.TARGET_COUNT_LONG_SURFACE) + "\n")
        fo.write("TARGET_COUNT_SQUARE_SURFACE=" + str(self.TARGET_COUNT_SQUARE_SURFACE) + "\n")
        fo.write("KEY_X=" + str(self.KEY_X) + "\n")
        fo.write("KEY_Y=" + str(self.KEY_Y) + "\n\n")
        for w in range(1,101):
            fo.write("[" + str(w) + "]\n")
            fo.write("wallF=")
            self.getXYandIcon("front")
            while self.x == self.KEY_X and self.y == self.KEY_Y:  # Stop overlap with key
                self.getXYandIcon("front")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                self.getXYandIcon("front")
                while self.x == self.KEY_X and self.y == self.KEY_Y:  # Stop overlap with key
                    self.getXYandIcon("front")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallB=")
            self.getXYandIcon("back")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                self.getXYandIcon("back")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallL=")
            self.getXYandIcon("left")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("left")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallR=")
            self.getXYandIcon("right")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("right")
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("ceiling=")
            self.getXYandIcon("ceiling")
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                self.getXYandIcon("ceiling")
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