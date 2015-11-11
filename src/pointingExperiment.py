from Tkinter import *
import math
from messageSender import *
import pygame
import scipy
import scipy.linalg
import numpy
import threading
from threading import Thread
import time
from pygame.locals import *
import datetime
import tkMessageBox
import tkSimpleDialog
from math import sqrt, fabs
import csv
from random import randint


class MyDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(master, text="User Name:").grid(row=0)
        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1  # initial focus

    def apply(self):
        user = self.e1.get()
        self.result = (user)

    def getResult(self):
        return self.result


class client:
    __slots__ = ['ppe']
    quit = False
    refreshrate = 0
    mainCur = None
    controlCur = None
    username = None
    currentTrackerData = ["", ""]
    targets = None  # An array of target positions each target has [0] - x  [1] - y  [2] - diameter  [3] - surface
    currentTarget = 0
    defaultTarget = True
    mouseTask = True
    planes = []
    wallgrids = [[[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]],

                 [[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]]]
    wallTargets = [[],[],[],[],[]]



    # Checks for mouse button and keyboard
    def getInput(self, get_point):
        pos = pygame.mouse.get_pos()  # mouse shift
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True
                return None
            elif event.type == pygame.KEYDOWN:
                pass
            if (self.mouseLock == True):
                # Runs if a mouse button has been depressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Runs if the mouse wheel is being rolled upwards
                    if event.button == 4:
                        pass
                    elif event.button == 5:
                        pass
                    # Runs if the middle mouse button is pressed
                    elif event.button == 2:
                        self.mClickTime = datetime.datetime.now()  # Saves the current time so that when the button is released click duration can be checked
                        pass
                    # Runs if the right mouse button is pressed
                    elif event.button == 3:
                        self.rClickTime = datetime.datetime.now()  # Saves the current time so that when the button is released click duration can be checked
                        pass
                    # runs if the left mouse button is pressed
                    elif event.button == 1:
                        self.lClickTime = datetime.datetime.now()  # Saves the current time so that when the button is released click duration can be checked
                        pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Runs if the left mouse button has been released
                    if (event.button == 1):
                        lClickRelTime = datetime.datetime.now()
                        elapsedSecs = (
                        lClickRelTime - self.lClickTime).total_seconds()  # Checks how long the button was depressed
                        if (elapsedSecs < 0.15):
                            pass
                        else:
                            pass
                    # Runs if the middle mouse button has been released
                    if (event.button == 2):
                        mClickRelTime = datetime.datetime.now()
                        elapsedSecs = (
                        mClickRelTime - self.mClickTime).total_seconds()  # Checks how long the button was depressed
                        if (elapsedSecs < 0.25):
                            self.mouseLock = False
                            pygame.mouse.set_visible(True)
                            self.master.focus_force()
                            '''self.sender.hideCursor(self.mainCur)'''
                        else:
                            pass

                    # Runs if the right mouse button has been released
                    if (event.button == 3):
                        rClickRelTime = datetime.datetime.now()
                        elapsedSecs = (
                        rClickRelTime - self.rClickTime).total_seconds()  # Checks how long the button was depressed
                        if (elapsedSecs < 0.15):
                            pass
                        else:
                            pass
        return None

    #  Returns a tuple containing the tracker data for the pointer and the head
    def getTrackerData(self):
        pointerTrackerData = self.currentTrackerData[0]
        pointerTrackerData = pointerTrackerData.split(";")
        for x in range(0, len(pointerTrackerData)):
            pointerTrackerData[x] = pointerTrackerData[x].split(",")
            for y in range(0, len(pointerTrackerData[x])):
                try:
                    pointerTrackerData[x][y] = float(pointerTrackerData[x][y])
                except:
                    pass
        if(len(self.currentTrackerData)>1):
            headTrackerData = self.currentTrackerData[1]
            headTrackerData = headTrackerData.split(";")
            for x in range(0, len(headTrackerData)):
                headTrackerData[x] = headTrackerData[x].split(",")
                for y in range(0, len(headTrackerData[x])):
                    try:
                        pointerTrackerData[x][y] = float(headTrackerData[x][y])
                    except:
                        pass
            return pointerTrackerData, headTrackerData
        return pointerTrackerData, None

    def segmentPlane(self, plane, rayOrigin, rayVector):
        # print "Plane = " + str(plane)
        planeNormal = scipy.array([plane[0][0], plane[0][1], plane[0][2]])
        planeOrigin = scipy.array([plane[1][0], plane[1][1], plane[1][2]])
        rayOrigin = scipy.array([rayOrigin[0], rayOrigin[1], rayOrigin[2]])
        rayVector = scipy.array([rayVector[0], rayVector[1], rayVector[2]])
        originDistance = rayOrigin - planeOrigin
        D = planeNormal.dot(rayVector)
        N = -planeNormal.dot(originDistance)
        if (scipy.fabs(D) < 0.00000001):
            if (N == 0):
                # print "Segment lies in plane! The laws of physics don't apply anymore! What do!?"
                return 2
            else:
                # print "No intersection. Almost exactly parallel to plane!"
                return 0
        rayDistanceProp = N / D
        self.intersect = rayOrigin + rayDistanceProp * rayVector
        if rayDistanceProp >= 0:
            return 1
        else:
            # print "Ray facing away from surface"
            return 3

    def length(self, v):
        return scipy.sqrt(v.dot(v))

    def M(self, axis, theta):
        return scipy.linalg.expm3(numpy.cross(numpy.eye(3), axis / scipy.linalg.norm(axis) * theta))

    def angleBetweenVectors(self, v1, v2):
        return math.acos(v1.dot(v2)/(sqrt(pow(v1[0],2) + pow(v1[1],2) + pow(v1[2],2))*sqrt(pow(v2[0],2) + pow(v2[1],2) + pow(v2[2],2))))

    def radToDeg(self, radians):
        return radians*(180/math.pi)

    def degToRad(self, degrees):
        return degrees*(math.pi/180)

    def rotateVector(self, v, axis, degrees):
        theta = self.degToRad(degrees)
        axis = self.normalizeVec(axis)
        M0 = self.M(axis, theta)
        v = self.normalizeVec(v)
        out = numpy.dot(M0, v)
        return out

    def distToAngle(self, dist):
        return dist*0.1

    def getHeadVerticalVec(self):
        data = self.getTrackerData()[0] #TODO MAKE 1
        a = scipy.array([data[3][0]-data[2][0], data[3][1]-data[2][1], data[3][2]-data[2][2]])
        b = scipy.array([data[4][0]-data[2][0], data[4][1]-data[2][1], data[4][2]-data[2][2]])
        normal = numpy.cross(a, b)
        return scipy.array([normal[0], normal[1], normal[2]])

    def getHeadForwardVec(self):
        data = self.getTrackerData()[0]#TODO MAKE 1
        return scipy.array([data[1][0], data[1][1], data[1][2]])

    def getHeadLoc(self):
        data = self.getTrackerData()[0]#TODO MAKE 1
        return scipy.array([data[0][0], data[0][1], data[0][2]])

    def getHeadHorizontalVec(self):
        return numpy.cross(self.getHeadVerticalVec(), self.getHeadForwardVec())

    # Returns vector after setting magnitude to 1
    def normalizeVec(self, vec):
        return vec/scipy.linalg.norm(vec)

    def projectOntoPlane(self, vec, plane):
        d = vec.dot(plane) / scipy.linalg.norm(plane)
        p = d * self.normalizeVec(plane)
        return vec - p

    # Loops until the program is closed and monitors mouse movement
    def mouseMovement(self):
        headUp = self.normalizeVec(self.getHeadVerticalVec())
        changeVert = 0
        changeHoriz = 0
        forVec = self.getHeadForwardVec()
        while (self.quit == False):
            time.sleep(1.0 / 60)
            if (self.mouseLock == True):
                if (self.mouseTask == True):
                    pos = pygame.mouse.get_pos()
                    xdist = (self.winWidth / 2) - pos[0]
                    ydist = (self.winHeight / 2) - pos[1]
                    if (not (xdist == 0 and ydist == 0)):
                        headUp = self.normalizeVec(self.getHeadVerticalVec())
                        forVec = self.getHeadForwardVec()
                        pygame.mouse.set_pos([self.winWidth / 2, self.winHeight / 2])
                        changeHoriz += self.distToAngle(xdist)
                        curVec = self.rotateVector(forVec, headUp, changeHoriz)
                        horizAxis = numpy.cross(headUp, curVec)
                        changeVert += -self.distToAngle(ydist)
                        curVec = self.rotateVector(curVec, horizAxis, changeVert)
                        intersections = [0, 0, 0, 0, 0]
                        mouseLocations = []
                        for x in range(0, len(self.planes)):
                            segCheck = self.segmentPlane(self.planes[x], self.getHeadLoc(), curVec)
                            if segCheck == 1:
                                intersections[x] = scipy.array([self.intersect[0], self.intersect[1], self.intersect[2]])
                                diagVec = intersections[x] - self.planes[x][2]
                                hVec = self.planes[x][3] - self.planes[x][2]
                                vVec = self.planes[x][5] - self.planes[x][2]
                                hdot = diagVec.dot(hVec)
                                vdot = diagVec.dot(vVec)
                                hVecDist = sqrt(pow(hVec[0], 2) + pow(hVec[1], 2) + pow(hVec[2], 2))
                                vVecDist = sqrt(pow(vVec[0], 2) + pow(vVec[1], 2) + pow(vVec[2], 2))
                                hproj = (hdot / pow(hVecDist, 2)) * hVec
                                vproj = (vdot / pow(vVecDist, 2)) * vVec
                                hProjDist = sqrt(pow(hproj[0], 2) + pow(hproj[1], 2) + pow(hproj[2], 2))
                                vProjDist = sqrt(pow(vproj[0], 2) + pow(vproj[1], 2) + pow(vproj[2], 2))
                                hProp = hProjDist / hVecDist
                                vProp = vProjDist / vVecDist
                                hvecangle = scipy.arccos(hdot / (self.length(diagVec) * self.length(hVec)))
                                hvecangle = numpy.rad2deg(hvecangle)
                                vvecangle = scipy.arccos(vdot / (self.length(diagVec) * self.length(vVec)))
                                vvecangle = numpy.rad2deg(vvecangle)
                                if (0 <= hProp <= 1) and (0 <= vProp <= 1) and hvecangle <= 90 and vvecangle <= 90:
                                    mouseLocations.append((hProp, vProp, x+1))
                                else:
                                    intersections[x] = 0
                        if len(mouseLocations) > 0:
                            self.sender.relocateCursor(self.curs[0], mouseLocations[0][0], 1.0 - mouseLocations[0][1],
                                                       "prop", mouseLocations[0][2])
                            self.sender.showCursor(self.curs[0])
                            if len(mouseLocations) > 1:
                                self.sender.relocateCursor(self.curs[1], mouseLocations[1][0], 1.0 - mouseLocations[1][1],
                                                           "prop", mouseLocations[1][2])
                                self.sender.showCursor(self.curs[1])
                            else:
                                self.sender.hideCursor(self.curs[1])
                        else:
                            self.sender.hideCursor(self.curs[0])
                            self.sender.hideCursor(self.curs[1])
                else:
                    intersections = [0, 0, 0, 0, 0]
                    mouseLocations = []
                    for x in range(0, len(self.planes)):
                        segCheck = self.segmentPlane(self.planes[x], self.getTrackerData()[0][0], self.getTrackerData()[0][1])
                        if segCheck == 1:
                            intersections[x] = scipy.array([self.intersect[0], self.intersect[1], self.intersect[2]])
                            diagVec = intersections[x] - self.planes[x][2]
                            hVec = self.planes[x][3] - self.planes[x][2]
                            vVec = self.planes[x][5] - self.planes[x][2]
                            hdot = diagVec.dot(hVec)
                            vdot = diagVec.dot(vVec)
                            hVecDist = sqrt(pow(hVec[0], 2) + pow(hVec[1], 2) + pow(hVec[2], 2))
                            vVecDist = sqrt(pow(vVec[0], 2) + pow(vVec[1], 2) + pow(vVec[2], 2))
                            hproj = (hdot / pow(hVecDist, 2)) * hVec
                            vproj = (vdot / pow(vVecDist, 2)) * vVec
                            hProjDist = sqrt(pow(hproj[0], 2) + pow(hproj[1], 2) + pow(hproj[2], 2))
                            vProjDist = sqrt(pow(vproj[0], 2) + pow(vproj[1], 2) + pow(vproj[2], 2))
                            hProp = hProjDist / hVecDist
                            vProp = vProjDist / vVecDist
                            hvecangle = scipy.arccos(hdot / (self.length(diagVec) * self.length(hVec)))
                            hvecangle = numpy.rad2deg(hvecangle)
                            vvecangle = scipy.arccos(vdot / (self.length(diagVec) * self.length(vVec)))
                            vvecangle = numpy.rad2deg(vvecangle)
                            if (0 <= hProp <= 1) and (0 <= vProp <= 1) and hvecangle <= 90 and vvecangle <= 90:
                                mouseLocations.append((hProp, vProp, x+1))
                            else:
                                intersections[x] = 0
                    if len(mouseLocations) > 0:
                        self.sender.relocateCursor(self.curs[0], mouseLocations[0][0], 1.0 - mouseLocations[0][1],
                                                   "prop", mouseLocations[0][2])
                        self.sender.showCursor(self.curs[0])
                        if len(mouseLocations) > 1:
                            self.sender.relocateCursor(self.curs[1], mouseLocations[1][0], 1.0 - mouseLocations[1][1],
                                                       "prop", mouseLocations[1][2])
                            self.sender.showCursor(self.curs[1])
                        else:
                            self.sender.hideCursor(self.curs[1])
                    else:
                        self.sender.hideCursor(self.curs[0])
                        self.sender.hideCursor(self.curs[1])

    # Locks the mouse so that the server can be controlled
    def LockMouse(self):
        self.mouseLock = True
        pygame.mouse.set_visible(False)
        self.sender.showCursor(self.curs[0])

    def serverInit(self):
        CONNECTION_LIST = []
        RECV_BUFFER = 4096
        PORT = 5043

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # server_socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)
        server_socket.bind(("localhost", PORT))
        server_socket.listen(10)

        CONNECTION_LIST.append(server_socket)

        print "Chat server started on port " + str(PORT)

        while 1:
            read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

            for sock in read_sockets:
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                else:
                    try:
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            tempTrackerData = str(data).split("$")  # Separate the pointer and head data
                            if tempTrackerData[0] != "":
                                self.currentTrackerData[0] = tempTrackerData[0]
                            if tempTrackerData[1] != "":
                                self.currentTrackerData[1] = tempTrackerData[1]
                    except:
                        print "Client (%s, %s) is offline" % addr
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue

        server_socket.close()

    # Defines the GUI
    def tkinthread(self):
        self.master = Tk()
        d = MyDialog(self.master)
        self.username = d.getResult()
        self.master.wm_title("Cursor Program GUI")
        self.frame = Frame(self.master)
        self.frame.pack()
        self.slogan = Button(self.frame, text="Control Projected Mouse (Middle Click to Release)",
                             command=self.LockMouse, width=40)
        self.slogan.pack(side=LEFT)
        self.master.mainloop()

    def assignRandomTargets(self, wallNo, noOfTargets):
        if 0 < wallNo <= 5:  # Checks that the wall number is valid (between 1 and 5)
            if noOfTargets <= 25:
                targets = []
                for x in range(0, noOfTargets):
                    foundSpace = False
                    while not foundSpace:
                        # Create random grid coordinates
                        xrand = randint(0, 4)
                        yrand = randint(0, 4)
                        hit = False
                        for y in range(0, len(targets)):
                            if targets[y][0] == xrand and targets[y][1] == yrand:
                                hit = True
                        if not hit:
                            foundSpace = True

                    # Convert grid coordinates to surface coordinates
                    realX = xrand*2/10.0+0.1
                    realY = 1-(yrand*2/10.0+0.1)
                    foundUnused = False
                    while not foundUnused:
                        fileNumber = randint(7, 144)
                        hit = False
                        for y in range(0, len(self.wallTargets)):
                            for z in range(0, len(self.wallTargets[y])):
                                if self.wallTargets[y][z][2] == fileNumber:
                                    hit = True
                        if not hit:
                            foundUnused = True
                    icon = self.sender.newTexRectangle(self.wallCanvases[wallNo-1], realX - 0.05, realY + 0.05, 0.1,
                                                       0.1, "prop", "img/" + str(fileNumber) + ".png")
                    targets.append((xrand, yrand, fileNumber, icon))
                self.wallTargets[wallNo-1] = targets
            else:
                print "You can't have that many targets"
        else:
            print "There is no wall " + str(wallNo)

    def removeWallTargets(self, wallNo):
        targets = self.wallTargets[wallNo-1]
        self.wallTargets[wallNo-1] = []
        for x in range(0, len(targets)):
            self.sender.removeElement(targets[x][3], self.wallCanvases[wallNo-1])

    # Sets up the surfaces which can be defined within the client
    def initGUI(self):
        self.wallCanvases = []
        self.wallCanvases.append(self.sender.newCanvas(1, 0, 1, 1, 1, "prop", "wall1"))
        self.assignRandomTargets(1, 25)
        '''self.wall2C = self.sender.newCanvas(2, 0, 1, 1, 1, "prop", "wall2")
        self.wall3C = self.sender.newCanvas(3, 0, 1, 1, 1, "prop", "wall3")
        self.wall4C = self.sender.newCanvas(4, 0, 1, 1, 1, "prop", "wall4")
        '''
        self.curs = []
        self.curs.append(self.sender.newCursor(1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(self.curs[0])
        self.curs.append(self.sender.newCursor(1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(self.curs[1])

    def loadWallCoordinates(self, filename):
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            self.planes = []
            content = []
            for row in reader:
                temp = []
                for x in range(0, len(row)):
                    temp.append(float(row[x]))
                temp = scipy.array([temp[0], temp[1], temp[2]])
                content.append(temp)
            # print str(content)
            self.planes.append([content[0], content[1], content[2], content[3], content[4], content[5]])
            self.planes.append([content[6], content[7], content[8], content[9], content[10], content[11]])
            self.planes.append([content[12], content[13], content[14], content[15], content[16], content[17]])
            self.planes.append([content[18], content[19], content[20], content[21], content[22], content[23]])

    # The main loop
    def __init__(self):
        tkinterThread = threading.Thread(target=self.tkinthread, args=())  # Creates the display thread
        tkinterThread.start()  # Starts the display thread

        thread = Thread(target=self.serverInit, args=())
        thread.start()

        self.sender = messageSender()
        self.winWidth = 320
        self.winHeight = 240

        # Initialise screen
        pygame.init()
        self.screen = pygame.display.set_mode((self.winWidth, self.winHeight))
        pygame.display.set_caption('Cursor Program')

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255, 255, 255))

        # Display some text
        self.font = pygame.font.Font(None, 36)

        self.splitid = 0

        # Blit everything to the screen
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        while (self.username == None):
            pass
        self.sender.login(self.username)
        self.sender.setapp("CursorApp")
        # self.sender.loadDefinedSurfaces("DEFAULT")
        self.loadWallCoordinates('layout.csv')
        self.initGUI()

        self.mouseLock = False
        pygame.mouse.set_visible(False)

        mouseThread = threading.Thread(target=self.mouseMovement, args=())  # Creates the display thread
        mouseThread.start()  # Starts the display thread

        if (self.quit == False):
            while (self.quit == False):
                self.background.fill((255, 255, 255))
                text = self.font.render("", 1, (10, 10, 10))
                textpos = text.get_rect()
                textpos.centerx = self.background.get_rect().centerx
                self.background.blit(text, textpos)
                self.getInput(False)
                self.screen.blit(self.background, (0, 0))
                pygame.display.flip()
                time.sleep(1 / 30)
        time.sleep(0.2)
        pygame.quit()


client()
