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

    POSSIBLE_C = [(4, 8), (5, 5), (2, 4), (4, 7), (3, 6)]
    POSSIBLE_L = [(5, 3), (8, 2), (3, 3), (5, 4), (9, 2)]
    POSSIBLE_R = [(4, 3), (6, 2), (3, 3), (5, 2), (3, 3)]
    POSSIBLE_F = [(4, 3), (2, 5), (4, 2), (3, 4), (5, 3)]
    POSSIBLE_B = [(2, 5), (4, 3), (3, 4), (4, 4), (5, 5)]

    x = 0
    y = 0
    icon = 0
    usedLocs = []
    usedIcons = []
    numberOfImages = 0
    availableImages = []
    total_target_count = TARGET_COUNT_LONG_SURFACE * 3 + TARGET_COUNT_SQUARE_SURFACE * 2
    debugCount = 0

    def getXYandIcon(self, wall, isTarget):
        xWidth = 0
        yWidth = 0
        possibleTargets = []
        if wall == "front":
            possibleTargets = self.POSSIBLE_F
            xWidth = self.FRONT_WIDE
            yWidth = self.FRONT_TALL
        elif wall == "back":
            possibleTargets = self.POSSIBLE_B
            xWidth = self.BACK_WIDE
            yWidth = self.BACK_TALL
        elif wall == "left":
            possibleTargets = self.POSSIBLE_L
            xWidth = self.LEFT_WIDE
            yWidth = self.LEFT_TALL
        elif wall == "right":
            possibleTargets = self.POSSIBLE_R
            xWidth = self.RIGHT_WIDE
            yWidth = self.RIGHT_TALL
        elif wall == "ceiling":
            possibleTargets = self.POSSIBLE_C
            xWidth = self.CEILING_WIDE
            yWidth = self.CEILING_TALL
        xPick = randint(1, xWidth)
        yPick = randint(1, yWidth)
        if not isTarget:
            while (xPick, yPick) in self.usedLocs or (xPick, yPick) in possibleTargets:
                xPick = randint(1, xWidth)
                yPick = randint(1, yWidth)
        else:
            while (xPick, yPick) not in possibleTargets:
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
        if isTarget:
            self.debugCount += 1

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
        fo = open("targets.ini", "wb")
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
            target = randint(0, self.total_target_count-1)
            count = 0
            fo.write("[" + str(w) + "]\n")
            fo.write("wallF=")
            targetIcon = ""
            if count != target:
                self.getXYandIcon("front", False)
                while self.x == self.KEY_X and self.y == self.KEY_Y:  # Stop overlap with key
                    self.getXYandIcon("front", False)
            else:
                self.getXYandIcon("front", True)
                targetIcon = self.icon
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            count += 1
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                if count != target:
                    self.getXYandIcon("front", False)
                    while self.x == self.KEY_X and self.y == self.KEY_Y:  # Stop overlap with key
                        self.getXYandIcon("front", False)
                else:
                    self.getXYandIcon("front", True)
                    targetIcon = self.icon
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
                count += 1
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallB=")
            if count != target:
                self.getXYandIcon("back", False)
            else:
                self.getXYandIcon("back", True)
                targetIcon = self.icon
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            count += 1
            for z in range(1, self.TARGET_COUNT_SQUARE_SURFACE):
                fo.write(";")
                if count != target:
                    self.getXYandIcon("back", False)
                else:
                    self.getXYandIcon("back", True)
                    targetIcon = self.icon
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
                count += 1
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallL=")
            if count != target:
                self.getXYandIcon("left", False)
            else:
                self.getXYandIcon("left", True)
                targetIcon = self.icon
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            count += 1
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                if count != target:
                    self.getXYandIcon("left", False)
                else:
                    self.getXYandIcon("left", True)
                    targetIcon = self.icon
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
                count += 1
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("wallR=")
            if count != target:
                self.getXYandIcon("right", False)
            else:
                self.getXYandIcon("right", True)
                targetIcon = self.icon
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            count += 1
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                if count != target:
                    self.getXYandIcon("right", False)
                else:
                    self.getXYandIcon("right", True)
                    targetIcon = self.icon
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
                count += 1
            fo.write("\n")
            self.clearUsedLocs()
            fo.write("ceiling=")
            if count != target:
                self.getXYandIcon("ceiling", False)
            else:
                self.getXYandIcon("ceiling", True)
                targetIcon = self.icon
            fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            count += 1
            for z in range(1, self.TARGET_COUNT_LONG_SURFACE):
                fo.write(";")
                if count != target:
                    self.getXYandIcon("ceiling", False)
                else:
                    self.getXYandIcon("ceiling", True)
                    targetIcon = self.icon
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
                count += 1
            fo.write("\n")
            fo.write("target=" + targetIcon)
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()
        fo.close()

gen = generator()
gen.buildFile()