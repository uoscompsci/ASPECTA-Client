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
    RIGHT_TALL = 6

    TARGET_COUNT_LONG_SURFACE = 8
    TARGET_COUNT_SQUARE_SURFACE = 4
    KEY_X = 2
    KEY_Y = 2

    POSSIBLE_C = [(4, 8), (5, 5), (2, 4), (3, 6)]
    POSSIBLE_L = [(3, 2), (4, 4), (7, 3), (8, 5)]
    POSSIBLE_R = [(3, 5), (4, 3), (7, 4), (8, 2)]
    POSSIBLE_F = [(2, 3), (4, 2), (3, 5), (5, 3)]
    POSSIBLE_B = [(2, 5), (4, 3), (3, 4), (5, 5)]

    target_counter = {}
    targetWall = ""

    x = 0
    y = 0
    icon = 0
    usedLocs = []
    usedIcons = []
    numberOfImages = 0
    availableImages = []
    total_target_count = TARGET_COUNT_LONG_SURFACE * 3 + TARGET_COUNT_SQUARE_SURFACE * 2
    debugCount = 0

    def getXYandIcon(self, wall, isTarget, synchronous, pointing):
        synch = "synch"
        if not synchronous:
            synch = "asynch"
        point = "point"
        if not pointing:
            point = "persp"
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
        keyBlocked = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if not isTarget:
            while (xPick, yPick) in self.usedLocs or (xPick, yPick) in possibleTargets or wall == "front" and (xPick, yPick) in keyBlocked:
                xPick = randint(1, xWidth)
                yPick = randint(1, yWidth)
        else:
            wallno = randint(0, len(self.walls)-1)
            layoutno = randint(0, len(self.POSSIBLE_F)-1)
            while self.target_counter[self.walls[wallno] + "-" + str(layoutno)][synch + "-" + point] == 3:
                wallno = randint(0, len(self.walls)-1)
                layoutno = randint(0, len(self.POSSIBLE_F)-1)
            self.target_counter[self.walls[wallno] + "-" + str(layoutno)][synch + "-" + point] += 1
            wallList = []
            if self.walls[wallno] == "front":
                wallList = self.POSSIBLE_F
            elif self.walls[wallno] == "back":
                wallList = self.POSSIBLE_B
            elif self.walls[wallno] == "left":
                wallList = self.POSSIBLE_L
            elif self.walls[wallno] == "right":
                wallList = self.POSSIBLE_R
            elif self.walls[wallno] == "ceiling":
                wallList = self.POSSIBLE_C
            xPick = wallList[layoutno][0]
            yPick = wallList[layoutno][1]
            self.targetWall = self.walls[wallno]
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
        reps = 3
        self.walls = ["ceiling", "front", "back", "left", "right"]
        for x in range(0, len(self.walls)):
            for y in range(0, len(self.POSSIBLE_F)):
                self.target_counter[self.walls[x] + "-" + str(y)] = {"synch-point": 0, "asynch-point": 0, "synch-persp": 0, "asynch-persp": 0}

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


        synchronous = True
        pointing = True
        for w in range(0, 60):
            fo.write("[" + str(w+1) + "]\n")
            self.getXYandIcon("ceiling", True, synchronous, pointing)
            targetx = self.x
            targety = self.y
            targetIcon = self.icon
            wall = self.targetWall
            ceilingTargetCount = self.TARGET_COUNT_LONG_SURFACE
            frontTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            backTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            rightTargetCount = self.TARGET_COUNT_LONG_SURFACE
            leftTargetCount = self.TARGET_COUNT_LONG_SURFACE
            if wall == "ceiling":
                ceilingTargetCount -= 1
            elif wall == "front":
                frontTargetCount -= 1
            elif wall == "back":
                backTargetCount -= 1
            elif wall == "left":
                leftTargetCount -= 1
            elif wall == "right":
                rightTargetCount -= 1

            fo.write("wallF=")
            first = True
            for z in range(0, frontTargetCount):
                if first:
                    if wall == "front":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("front", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallB=")
            first = True
            for z in range(0, backTargetCount):
                if first:
                    if wall == "back":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("back", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallL=")
            first = True
            for z in range(0, leftTargetCount):
                if first:
                    if wall == "left":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("left", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallR=")
            first = True
            for z in range(0, rightTargetCount):
                if first:
                    if wall == "right":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("right", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("ceiling=")
            first = True
            for z in range(0, ceilingTargetCount):
                if first:
                    if wall == "ceiling":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("ceiling", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            fo.write("target=" + targetIcon)
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()

        for w in range(60, 120):
            synchronous = False
            fo.write("[" + str(w+1) + "]\n")
            self.getXYandIcon("ceiling", True, synchronous, pointing)
            targetx = self.x
            targety = self.y
            targetIcon = self.icon
            wall = self.targetWall
            ceilingTargetCount = self.TARGET_COUNT_LONG_SURFACE
            frontTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            backTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            rightTargetCount = self.TARGET_COUNT_LONG_SURFACE
            leftTargetCount = self.TARGET_COUNT_LONG_SURFACE
            if wall == "ceiling":
                ceilingTargetCount -= 1
            elif wall == "front":
                frontTargetCount -= 1
            elif wall == "back":
                backTargetCount -= 1
            elif wall == "left":
                leftTargetCount -= 1
            elif wall == "right":
                rightTargetCount -= 1

            fo.write("wallF=")
            first = True
            for z in range(0, frontTargetCount):
                if first:
                    if wall == "front":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("front", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallB=")
            first = True
            for z in range(0, backTargetCount):
                if first:
                    if wall == "back":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("back", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallL=")
            first = True
            for z in range(0, leftTargetCount):
                if first:
                    if wall == "left":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("left", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallR=")
            first = True
            for z in range(0, rightTargetCount):
                if first:
                    if wall == "right":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("right", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("ceiling=")
            first = True
            for z in range(0, ceilingTargetCount):
                if first:
                    if wall == "ceiling":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("ceiling", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            fo.write("target=" + targetIcon)
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()

        for w in range(120, 180):
            synchronous = True
            pointing = False
            fo.write("[" + str(w+1) + "]\n")
            self.getXYandIcon("ceiling", True, synchronous, pointing)
            targetx = self.x
            targety = self.y
            targetIcon = self.icon
            wall = self.targetWall
            ceilingTargetCount = self.TARGET_COUNT_LONG_SURFACE
            frontTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            backTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            rightTargetCount = self.TARGET_COUNT_LONG_SURFACE
            leftTargetCount = self.TARGET_COUNT_LONG_SURFACE
            if wall == "ceiling":
                ceilingTargetCount -= 1
            elif wall == "front":
                frontTargetCount -= 1
            elif wall == "back":
                backTargetCount -= 1
            elif wall == "left":
                leftTargetCount -= 1
            elif wall == "right":
                rightTargetCount -= 1

            fo.write("wallF=")
            first = True
            for z in range(0, frontTargetCount):
                if first:
                    if wall == "front":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("front", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallB=")
            first = True
            for z in range(0, backTargetCount):
                if first:
                    if wall == "back":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("back", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallL=")
            first = True
            for z in range(0, leftTargetCount):
                if first:
                    if wall == "left":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("left", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallR=")
            first = True
            for z in range(0, rightTargetCount):
                if first:
                    if wall == "right":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("right", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("ceiling=")
            first = True
            for z in range(0, ceilingTargetCount):
                if first:
                    if wall == "ceiling":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("ceiling", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            fo.write("target=" + targetIcon)
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()

        for w in range(180, 240):
            synchronous = False
            fo.write("[" + str(w+1) + "]\n")
            self.getXYandIcon("ceiling", True, synchronous, pointing)
            targetx = self.x
            targety = self.y
            targetIcon = self.icon
            wall = self.targetWall
            ceilingTargetCount = self.TARGET_COUNT_LONG_SURFACE
            frontTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            backTargetCount = self.TARGET_COUNT_SQUARE_SURFACE
            rightTargetCount = self.TARGET_COUNT_LONG_SURFACE
            leftTargetCount = self.TARGET_COUNT_LONG_SURFACE
            if wall == "ceiling":
                ceilingTargetCount -= 1
            elif wall == "front":
                frontTargetCount -= 1
            elif wall == "back":
                backTargetCount -= 1
            elif wall == "left":
                leftTargetCount -= 1
            elif wall == "right":
                rightTargetCount -= 1

            fo.write("wallF=")
            first = True
            for z in range(0, frontTargetCount):
                if first:
                    if wall == "front":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("front", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallB=")
            first = True
            for z in range(0, backTargetCount):
                if first:
                    if wall == "back":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("back", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallL=")
            first = True
            for z in range(0, leftTargetCount):
                if first:
                    if wall == "left":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("left", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("wallR=")
            first = True
            for z in range(0, rightTargetCount):
                if first:
                    if wall == "right":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("right", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")

            fo.write("ceiling=")
            first = True
            for z in range(0, ceilingTargetCount):
                if first:
                    if wall == "ceiling":
                        fo.write(str(targetx) + "," + str(targety) + ":" + targetIcon + ";")
                    first = False
                else:
                    fo.write(";")
                self.getXYandIcon("ceiling", False, synchronous, pointing)
                fo.write(str(self.x) + "," + str(self.y) + ":" + self.icon)
            fo.write("\n")
            fo.write("target=" + targetIcon)
            fo.write("\n\n")
            self.clearUsedLocs()
            self.clearUsedIcons()
        fo.close()

gen = generator()
gen.buildFile()