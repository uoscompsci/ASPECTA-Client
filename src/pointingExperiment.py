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
    CANVAS1PROJ = 1
    CANVAS2PROJ = 1
    CANVAS3PROJ = 1
    CANVAS4PROJ = 1
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
    wall2ProjectorSurface = {}
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
                        headTrackerData[x][y] = float(headTrackerData[x][y])
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
        temp = v1.dot(v2)/(sqrt(pow(v1[0], 2) + pow(v1[1], 2) + pow(v1[2], 2))*sqrt(pow(v2[0], 2) + pow(v2[1], 2) + pow(v2[2], 2)))
        if temp > 1.0:  # Stops tiny rounding errors causing value to be slightly above 1.0 from causing problems
            temp = 1.0
        return self.radToDeg(math.acos(temp))

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

    def distBetweenPoints(self, point1, point2):
        return sqrt(pow((point1[0]-point2[0]),2) + pow((point1[1]-point2[1]),2) + pow((point1[2]-point2[2]),2))

    def getHeadAxes(self):
        data = self.getTrackerData()[1]

        #Retrieve the points on the trackers and place them in an array
        point1 = scipy.array([data[0][0], data[0][1], data[0][2]])
        point2 = scipy.array([data[1][0], data[1][1], data[1][2]])
        point3 = scipy.array([data[2][0], data[2][1], data[2][2]])
        points = [point1, point2, point3]

        #Get the indexes of the closest two points in the array
        minlength = -1
        minpoint1Index = 0
        minpoint2Index = 0
        for x in range(0,len(points)):
            for y in range(0,len(points)):
                distance = self.distBetweenPoints(points[x], points[y])
                if(distance!=0):
                    if(distance < minlength or minlength == -1):
                        minlength = distance
                        minpoint1Index = x
                        minpoint2Index = y

        #Save the head location as the point directly in the middle of the closest points
        headLoc = (points[minpoint1Index]+points[minpoint2Index])/2

        #Find the preliminary upward vector to use as a rotation axis to find the forward vector
        vec1 = points[0]-points[1]
        vec2 = points[2]-points[1]
        normal = numpy.cross(vec1, vec2)
        if(normal[1]<0):
            normal[0] = -normal[0]
            normal[1] = -normal[1]
            normal[2] = -normal[2]
        preUp = scipy.array([normal[0], normal[1], normal[2]])

        #Define the two potential forward vectors
        forwardVecTest1 = self.rotateVector(points[minpoint2Index]-points[minpoint1Index],preUp,90)
        forwardVecTest2 = self.rotateVector(points[minpoint2Index]-points[minpoint1Index],preUp,-90)

        #Work out the index of the extra tracker ball
        extraPointIndex = 0
        if(minpoint1Index==0 or minpoint2Index==0):
            extraPointIndex = 1
            if(minpoint1Index==1 or minpoint2Index==1):
                extraPointIndex = 2

        #Work out which forward vector is the true one (the one which doesn't point in the direction of the extra ball)
        forwardVec = forwardVecTest2
        location1 = headLoc+forwardVecTest1
        location2 = headLoc+forwardVecTest2
        distance1 = self.distBetweenPoints(location1, points[extraPointIndex])
        distance2 = self.distBetweenPoints(location2, points[extraPointIndex])
        if distance2<distance1:
            forwardVec = forwardVecTest1

        #Realign the upward vector to ensure it is perpendicular to the forward vector
        upwardVec = self.normalizeVec(self.projectOntoPlane(preUp, forwardVec))

        #Define the horizontal vector as the cross product of the forward vector and upward vector
        horizontalVec = self.normalizeVec(numpy.cross(upwardVec, forwardVec))

        #Return all the head details
        return headLoc, forwardVec, upwardVec, horizontalVec

    # Returns vector after setting magnitude to 1
    def normalizeVec(self, vec):
        return vec/scipy.linalg.norm(vec)

    #http://www.maplesoft.com/support/help/Maple/view.aspx?path=MathApps%2FProjectionOfVectorOntoPlane
    def projectOntoPlane(self, vec, planeNormal):
        d = vec.dot(planeNormal) / pow(scipy.linalg.norm(planeNormal), 2)
        p = d * self.normalizeVec(planeNormal)
        return vec - p

    def getRotationFromVectors(self, destinationVec, forwardVec, horizontalPlaneNormal, verticalPlaneNormal):
        longitudeVec = self.projectOntoPlane(destinationVec, horizontalPlaneNormal)  # Projects the vector onto the horizontal plane
        changeHoriz = self.angleBetweenVectors(longitudeVec, forwardVec)  # Gets horizontal component of angle to cursor

        #  Figure out if angle is positive or negative and update as appropriate
        cross = scipy.cross(forwardVec, longitudeVec)
        if horizontalPlaneNormal.dot(cross) < 0:
            changeHoriz = -changeHoriz

        verticalPlaneNormal = self.rotateVector(verticalPlaneNormal, horizontalPlaneNormal, changeHoriz)
        forwardVec = self.rotateVector(forwardVec, horizontalPlaneNormal, changeHoriz)

        lattitudeVec = self.projectOntoPlane(destinationVec, verticalPlaneNormal)  # Projects the vector onto the vertical plane
        changeVert = self.angleBetweenVectors(lattitudeVec, forwardVec)  # Gets vertical component of angle to cursor

        #  Figure out if angle is positive or negative and update as appropriate
        cross = scipy.cross(forwardVec, lattitudeVec)
        if verticalPlaneNormal.dot(cross) < 0:
            changeVert = -changeVert

        return changeHoriz, changeVert

    def rotateForwardVectorByMouse(self, mouseXDiff, mouseYDiff, existingHorizRotation, existingVertRotation, forwardVec, upwardVec):
        if mouseXDiff != 0:
            existingHorizRotation += self.distToAngle(mouseXDiff)  # Updates the horizontal angle according to mouse movement readings
        curVec = self.rotateVector(forwardVec, upwardVec, existingHorizRotation)  # Rotates the vector about the vertical axis by the horizontal angle
        horizAxis = numpy.cross(upwardVec, curVec)  # Gets the new horizontal axis
        if mouseYDiff != 0:
            existingVertRotation += -self.distToAngle(mouseYDiff)  # Updates the horizontal angle according to mouse movement readings
        curVec = self.rotateVector(curVec, horizAxis, existingVertRotation)  # Rotates the vector about the horizontal axis by the vertical angle
        return curVec

    def getNewVec(self, axes, oldIntersectVec, xdist, ydist):
        changeHoriz, changeVert = self.getRotationFromVectors(oldIntersectVec, axes[1], axes[2], axes[3])
        curVec = self.rotateForwardVectorByMouse(xdist, ydist, changeHoriz, changeVert, axes[1], axes[2])
        return curVec

    # Loops until the program is closed and monitors mouse movement
    def mouseMovement(self):
        axes = self.getHeadAxes()
        curVec = axes[1]
        lastHeadLoc = axes[0]
        while (self.quit == False):
            time.sleep(1.0 / 60)
            if (self.mouseLock == True):
                if (self.mouseTask == True): # Runs if it is mouse movement that is to control the cursor (perspective)
                    pos = pygame.mouse.get_pos()
                    xdist = (self.winWidth / 2) - pos[0]
                    ydist = (self.winHeight / 2) - pos[1]
                    intersections = None
                    if (not (xdist == 0 and ydist == 0)):
                        for x in range(0, len(self.planes)):  # Finds where the last intersect point was
                            segCheck = self.segmentPlane(self.planes[x], lastHeadLoc, curVec)
                            if(segCheck == 1):
                                break
                        oldIntersect = self.intersect  # Saves the last intersect point
                        axes = self.getHeadAxes()
                        lastHeadLoc = axes[0]  # From now on the current head location is used
                        oldIntersectVec = self.normalizeVec(oldIntersect - lastHeadLoc)  # Gets the vector that now points from the head to cursor
                        pygame.mouse.set_pos([self.winWidth / 2, self.winHeight / 2])  # Returns cursor to the middle of the window
                        curVec = self.getNewVec(axes, oldIntersectVec, xdist, ydist)
                        intersections = [1, 1, 1, 1]
                        mouseLocations = []
                        for x in range(0, len(self.planes)):
                            segCheck = self.segmentPlane(self.planes[x], lastHeadLoc, curVec)
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
                                    mouseLocations.append((hProp, vProp, self.wall2ProjectorSurface[x+1]))
                                else:
                                    intersections[x] = 0
                        for x in range(0,len(mouseLocations)):
                            if mouseLocations[x][2][0]==1: #if the cursor is on surface 1
                                self.sender.hideCursor(2, self.curs[2+x])
                                self.sender.relocateCursor(1, self.curs[0+x], mouseLocations[x][0], 1.0-mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                                self.sender.showCursor(1, self.curs[0+x])
                            elif mouseLocations[x][2][0]==2: #if the cursor is on surface 2
                                self.sender.hideCursor(1, self.curs[0+x])
                                self.sender.relocateCursor(2, self.curs[2+x], mouseLocations[x][0], 1.0-mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                                self.sender.showCursor(2, self.curs[2+x])
                else: # Runs if it is pointing that is to control the cursor
                    intersections = [1, 1, 1, 1]
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
                                mouseLocations.append((hProp, vProp, self.wall2ProjectorSurface[x+1]))
                            else:
                                intersections[x] = 0
                    for x in range(0,len(mouseLocations)):
                        if mouseLocations[x][2][0]==1: #if the cursor is on surface 1
                            self.sender.hideCursor(2, self.curs[2+x])
                            self.sender.relocateCursor(1, self.curs[0+x], mouseLocations[x][0], 1.0-mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                            self.sender.showCursor(1, self.curs[0+x])
                        elif mouseLocations[x][2][0]==2: #if the cursor is on surface 2
                            self.sender.hideCursor(1, self.curs[0+x])
                            self.sender.relocateCursor(2, self.curs[2+x], mouseLocations[x][0], 1.0-mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                            self.sender.showCursor(2, self.curs[2+x])

    # Locks the mouse so that the server can be controlled
    def LockMouse(self):
        self.mouseLock = True
        pygame.mouse.set_visible(False)
        self.sender.showCursor(1, self.curs[0])

    def wall2proj(self, wall):
        return self.wall2proj[wall]


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
        self.master.wm_title("Pointing Experiment GUI")
        self.frame = Frame(self.master)
        self.frame.pack()
        self.slogan = Button(self.frame, text="Control Projected Mouse (Middle Click to Release)",
                             command=self.LockMouse, width=40)
        self.slogan.pack(side=LEFT)
        self.master.mainloop()

    '''def assignRandomTargets(self, wallNo, noOfTargets):
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
                    icon = self.sender.newTexRectangle(1, self.wallCanvases[wallNo-1], realX - 0.05, realY + 0.05, 0.1,
                                                       0.1, "prop", "img/" + str(fileNumber) + ".png")
                    targets.append((xrand, yrand, fileNumber, icon))
                self.wallTargets[wallNo-1] = targets
            else:
                print "You can't have that many targets"
        else:
            print "There is no wall " + str(wallNo)'''

    def drawTarget(self, wallNo, x, y, icon):
        realX, realY = self.gridCoordToPropCenter(x, y)
        projector, canvas = self.targetWallToRoom(wallNo)
        target = self.sender.newTexRectangle(projector, canvas, realX - 0.05, realY + 0.05, 0.1, 0.1, "prop", "img/" + str(icon) + ".png")
        return target

    def drawLayout(self, layoutNo):
        dest = self.targets[layoutNo]['target']
        location = None
        wallTargets = self.targets[layoutNo]['wall1']
        for x in range(0, len(wallTargets)):
            target = wallTargets[x]
            if int(dest) == int(target[1]):
                location = target[0]
            self.drawTarget(0, target[0][0], target[0][1], target[1]) #TODO STATE WALL NO
        wallTargets = self.targets[layoutNo]['wall2']
        for x in range(0, len(wallTargets)):
            target = wallTargets[x]
            if int(dest) == int(target[1]):
                location = target[0]
            self.drawTarget(1, target[0][0], target[0][1], target[1]) #TODO STATE WALL NO
        wallTargets = self.targets[layoutNo]['wall3']
        for x in range(0, len(wallTargets)):
            target = wallTargets[x]
            if int(dest) == int(target[1]):
                location = target[0]
            self.drawTarget(2, target[0][0], target[0][1], target[1]) #TODO STATE WALL NO
        wallTargets = self.targets[layoutNo]['wall4']
        for x in range(0, len(wallTargets)):
            target = wallTargets[x]
            if int(dest) == int(target[1]):
                location = target[0]
            self.drawTarget(3, target[0][0], target[0][1], target[1]) #TODO STATE WALL NO
        wallTargets = self.targets[layoutNo]['ceiling']
        for x in range(0, len(wallTargets)):
            target = wallTargets[x]
            if int(dest) == int(target[1]):
                location = target[0]
            self.drawTarget(4, target[0][0], target[0][1], target[1]) #TODO STATE WALL NO
        return (location[0]-1, location[1]-1)

    def isHit(self, mouseCanvas, mouseCoor, targetCanvas, targetLoc):
        canvasNo = self.wallCanvases(mouseCanvas)[1]
        projectorNo = self.wallCanvases(mouseCanvas)[0]
        canvasWidth = self.sender.getCanvasWidth(projectorNo, canvasNo)
        canvasHeight = self.sender.getCanvasHeight(projectorNo, canvasNo)
        targetXProp, targetYProp = self.gridCoordToPropCenter(targetLoc[0], targetLoc[1])
        targetXReal = targetXProp * canvasWidth
        targetYReal = targetYProp * canvasHeight
        targetWidth = 0.1 * canvasWidth
        targetHeight = 0.1 * canvasHeight
        if mouseCoor[0]>targetXReal and mouseCoor[0]<(targetXReal+targetWidth):
            if mouseCoor[1]>targetYReal and mouseCoor[1]<(targetYReal+targetHeight):
                return True
        return False

    #self.angleBetweenVectors
    # Give grid coordinates and walls of start and end points to compute rotational distance between edges of start point and end point
    def getRotationalDists(self, startWall, startX, startY, targetWall, targetGridX, targetGridY):
        start, target = self.getStartAndTargetLocs(startWall, startX, startY, targetWall, targetGridX, targetGridY)
        headLoc = self.getHeadAxes()[0]
        startVec = start-headLoc
        targetVec = target-headLoc
        return self.angleBetweenVectors(startVec, targetVec)

    #return horizontal and vertical distances separately
    def getPlanarDists(self, startWall, startX, startY, targetWall, targetGridX, targetGridY):
        if(targetWall != REAR_WALL):
            if(targetWall == CEILING):
                part1 = self.getSurfaceWidthRemUp(startX, startY, FRONT_WALL)
                part2 = self.getSurfaceWidthRemDown(targetGridX, targetGridY, CEILING) #TODO CHECK WHAT START AND TARGET ARE THIS IS NOT CORRECT
            elif(targetWall == LEFT_WALL):
                part1 = self.getSurfaceWidthRemLeft(startX, startY, FRONT_WALL)
                part2 = self.getSurfaceWidthRemRight(targetGridX, targetGridY, LEFT_WALL)
            elif(targetWall == RIGHT_WALL):
                part1 = self.getSurfaceWidthRemRight(startX, startY, FRONT_WALL)
                part2 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY. RIGHT_WALL)
            else:
                print "Invalid target wall"
        else:
            #Calculate distance across ceiling
            part1 = self.getSurfaceWidthRemUp(startX, startX, FRONT_WALL)
            part2 = CEILING_LENGTH
            part3 = self.getSurfaceWidthRemUp(targetGridX, targetGridY, REAR_WALL)
            distanceCeiling = part1 + part2 + part3

            #Calculate distance across floor
            part1 = self.getSurfaceWidthRemDown(startX, startX, FRONT_WALL)
            part2 = FLOOR_LENGTH
            part3 = self.getSurfaceWidthRemDown(targetGridX, targetGridY, REAR_WALL)
            distanceFloor = part1 + part2 + part3

            #Calculate distance across left wall
            part1 = self.getSurfaceWidthRemLeft(startX, startX, FRONT_WALL)
            part2 = LEFT_LENGTH
            part3 = self.getSurfaceWidthRemRight(targetGridX, targetGridY, REAR_WALL)
            distanceLeft = part1 + part2 + part3

            #Calculate distance across right wall
            part1 = self.getSurfaceWidthRemRight(startX, startX, FRONT_WALL)
            part2 = RIGHT_LENGTH
            part3 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY, REAR_WALL)
            distanceRight = part1 + part2 + part3

            #Find which path is shortest
            shortest = distanceCeiling
            shortestStr = "ceiling"
            if distanceFloor < shortest:
                shortest = distanceFloor
                shortestStr = "floor"
            if distanceLeft < shortest:
                shortest = distanceLeft
                shortestStr = "left"
            if distanceRight < shortest:
                shortest = distanceRight
                shortestStr = "right"

            #Calculate horizontal distance component

            #TODO distance remainder on current wall + side wall length + distance on target wall

    def getDirectDists(self, startWall, startX, startY, targetWall, targetGridX, targetGridY):
        start, target = self.getStartAndTargetLocs(startWall, startX, startY, targetWall, targetGridX, targetGridY)
        return self.distBetweenPoints(start, target)

    def getSurfaceWidthRemLeft(self, pointX, pointY, wall):
        realPointX, realPointY = self.gridCoordToPropCenter(pointX, pointY)
        realEdgeX, realEdgeY = 0, realPointY
        wallTL = self.planes[wall][0][2]
        wallTR = self.planes[wall][0][3]# TODO Implement
        wallBL = self.planes[wall][0][5]
        pointHVec = wallTR - wallTL * realPointX
        pointVVec = wallBL - wallTL * realPointY
        edgeHVec = wallTR - wallTL * realEdgeX
        edgeVVec = wallBL - wallTL * realEdgeY
        point = wallTL + pointHVec + pointVVec
        edge = wallTL + edgeHVec + edgeVVec
        return self.distBetweenPoints(point, edge)

    def getSurfaceWidthRemRight(self, pointX, pointY, wall):
        realPointX, realPointY = self.gridCoordToPropCenter(pointX, pointY)
        realEdgeX, realEdgeY = 1, realPointY
        wallTL = self.planes[wall][0][2]
        wallTR = self.planes[wall][0][3]
        wallBL = self.planes[wall][0][5]
        pointHVec = wallTR - wallTL * realPointX
        pointVVec = wallBL - wallTL * realPointY
        edgeHVec = wallTR - wallTL * realEdgeX
        edgeVVec = wallBL - wallTL * realEdgeY
        point = wallTL + pointHVec + pointVVec
        edge = wallTL + edgeHVec + edgeVVec
        return self.distBetweenPoints(point, edge)

    def getSurfaceWidthRemUp(self, pointX, pointY, wall):
        realPointX, realPointY = self.gridCoordToPropCenter(pointX, pointY)
        realEdgeX, realEdgeY = realPointX, 1 #TODO check if 1 is top
        wallTL = self.planes[wall][0][2]
        wallTR = self.planes[wall][0][3]
        wallBL = self.planes[wall][0][5]
        pointHVec = wallTR - wallTL * realPointX
        pointVVec = wallBL - wallTL * realPointY
        edgeHVec = wallTR - wallTL * realEdgeX
        edgeVVec = wallBL - wallTL * realEdgeY
        point = wallTL + pointHVec + pointVVec
        edge = wallTL + edgeHVec + edgeVVec
        return self.distBetweenPoints(point, edge)

    def getSurfaceWidthRemDown(self, pointX, pointY, wall):
        realPointX, realPointY = self.gridCoordToPropCenter(pointX, pointY)
        realEdgeX, realEdgeY = realPointX, 0  #TODO check if 0 is bottom
        wallTL = self.planes[wall][0][2]
        wallTR = self.planes[wall][0][3]
        wallBL = self.planes[wall][0][5]
        pointHVec = wallTR - wallTL * realPointX
        pointVVec = wallBL - wallTL * realPointY
        edgeHVec = wallTR - wallTL * realEdgeX
        edgeVVec = wallBL - wallTL * realEdgeY
        point = wallTL + pointHVec + pointVVec
        edge = wallTL + edgeHVec + edgeVVec
        return self.distBetweenPoints(point, edge)


    # Get the real world locations of the start and target points
    def getStartAndTargetLocs(self, startWall, startX, startY, targetWall, targetGridX, targetGridY):
        # Gather the proportional coordinates for the start and target points
        realStartX, realStartY = self.gridCoordToPropCenter(startX, startY)
        realTargetX, realTargetY = self.gridCoordToPropCenter(targetGridX, targetGridY)
        # Get the 3D real world coordinates for the top left, bottom right and bottom left of each surface
        startWallTL = self.planes[startWall][0][2]
        startWallTR = self.planes[startWall][0][3]
        startWallBL = self.planes[startWall][0][5]
        targetWallTL = self.planes[targetWall][0][2]
        targetWallTR = self.planes[targetWall][0][3]
        targetWallBL = self.planes[targetWall][0][5]
        # Calculate the horizontal and vertical vectors that run along the top and left side of the walls and then convert them to the vectors to the start and target.
        startHVec = startWallTR - startWallTL * realStartX
        startVVec = startWallBL - startWallTL * realStartY
        targetHVec = targetWallTR - targetWallTL * realTargetX
        targetVVec = targetWallBL - targetWallTL * realTargetY
        # Use the calculated vectors to find the start and target 3D real world coordinates.
        start = startWallTL+startHVec+startVVec
        target = targetWallTL+targetHVec+targetVVec
        return start, target

    def gridCoordToPropCenter(self, x, y):
        x -= 1
        y -= 1
        x = x*2/10.0+0.1
        y = 1 - (y*2/10/0+0.1)
        return (x, y)

    def removeWallTargets(self, wallNo):
        targets = self.wallTargets[wallNo-1]
        self.wallTargets[wallNo-1] = []
        for x in range(0, len(targets)):
            self.sender.removeElement(self.wallCanvases[wallNo-1][0], targets[x][3], self.wallCanvases[wallNo-1][1])

    # Sets up the surfaces which can be defined within the client
    def initGUI(self):
        self.wallCanvases = []
        self.wallCanvases.append((self.CANVAS1PROJ, self.sender.newCanvas(self.CANVAS1PROJ, 1, 0, 1, 1, 1, "prop", "wall1")))
        self.assignRandomTargets(1, 25)
        self.wallCanvases.append((self.CANVAS2PROJ, self.sender.newCanvas(self.CANVAS2PROJ, 2, 0, 1, 1, 1, "prop", "wall2")))
        self.wallCanvases.append((self.CANVAS3PROJ, self.sender.newCanvas(self.CANVAS3PROJ, 3, 0, 1, 1, 1, "prop", "wall3")))
        self.wallCanvases.append((self.CANVAS4PROJ, self.sender.newCanvas(self.CANVAS4PROJ, 4, 0, 1, 1, 1, "prop", "wall4")))
        self.curs = []
        self.curs.append(self.sender.newCursor(1, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(1, self.curs[0])
        self.curs.append(self.sender.newCursor(1, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(1, self.curs[1])
        self.curs.append(self.sender.newCursor(2, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(2, self.curs[0])
        self.curs.append(self.sender.newCursor(2, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(2, self.curs[1])

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
            self.planes.append([content[24], content[25], content[26], content[27], content[28], content[29]])

    # The main loop
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        temp = parser.get('RoomSetup', 'wall1Surface')
        temp = temp.split(";")
        self.wall2ProjectorSurface[1] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'wall2Surface')
        temp = temp.split(";")
        self.wall2ProjectorSurface[2] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'wall3Surface')
        temp = temp.split(";")
        self.wall2ProjectorSurface[3] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'wall4Surface')
        temp = temp.split(";")
        self.wall2ProjectorSurface[4] = (int(temp[0]), int(temp[1]))

        self.targets = Targets()
        self.targets.parseFile("targets.ini")

        self.drawLayout(1)


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

class Targets:
    NO_TARGETS_WIDE = None
    NO_TARGETS_TALL = None
    NO_TARGETS_DEEP = None
    TARGET_COUNT_LONG_SURFACE = None
    TARGET_COUNT_SQUARE_SURFACE = None
    KEY_X = None
    KEY_Y = None

    def stringToTargetArray(self, surfaceString):
        surface = surfaceString.split(";")
        for x in range(0,len(surface)):
            surface[x] = surface[x].split(":")
            temp = surface[x][0].split(",")
            surface[x][0] = (int(temp[0]), int(temp[1]))
        return surface

    def parseFile(self, filename):
        targetParser = SafeConfigParser()
        targetParser.read(filename)

        # Get all the configuration details from the targets.ini file
        self.NO_TARGETS_WIDE = int(targetParser.get("configuration", "NO_TARGETS_WIDE"))
        self.NO_TARGETS_TALL = int(targetParser.get("configuration", "NO_TARGETS_TALL"))
        self.NO_TARGETS_DEEP = int(targetParser.get("configuration", "NO_TARGETS_DEEP"))
        self.TARGET_COUNT_LONG_SURFACE = int(targetParser.get("configuration", "TARGET_COUNT_LONG_SURFACE"))
        self.TARGET_COUNT_SQUARE_SURFACE = int(targetParser.get("configuration", "TARGET_COUNT_SQUARE_SURFACE"))
        self.KEY_X = int(targetParser.get("configuration", "KEY_X"))
        self.KEY_Y = int(targetParser.get("configuration", "KEY_Y"))

        # Get all the target locations from the targets.ini file
        self.targets = {}
        for x in range(1,101):
            wall1Str = targetParser.get(str(x), 'wallF')
            wall2Str = targetParser.get(str(x), 'wallB')
            wall3Str = targetParser.get(str(x), 'wallL')
            wall4Str = targetParser.get(str(x), 'wallR')
            ceilingStr = targetParser.get(str(x), 'ceiling')
            self.targets[x] = {}
            self.targets[x]['target'] = targetParser.get(str(x), 'target')
            self.targets[x]['wallF'] = self.stringToTargetArray(wall1Str)
            self.targets[x]['wallB'] = self.stringToTargetArray(wall2Str)
            self.targets[x]['wallL'] = self.stringToTargetArray(wall3Str)
            self.targets[x]['wallR'] = self.stringToTargetArray(wall4Str)
            self.targets[x]['ceiling'] = self.stringToTargetArray(ceilingStr)

    def getTargetsWide(self):
        return self.NO_TARGETS_WIDE

    def getTargetsTall(self):
        return self.NO_TARGETS_TALL

    def getTargetsDeep(self):
        return self.NO_TARGETS_DEEP

    def getTargetCountLongSurface(self):
        return self.TARGET_COUNT_LONG_SURFACE

    def getTargetCountSquareSurface(self):
        return self.TARGET_COUNT_SQUARE_SURFACE

    def getTargetKeyLocation(self):
        return self.KEY_X, self.KEY_Y

    def getTargetIcon(self, layout):
        return self.targets[layout]['target']

    def getTargetLocation(self, layout):
        for x in range(0, self.TARGET_COUNT_SQUARE_SURFACE):
            target = self.targets[layout]["wallF"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "Front"
        for x in range(0, self.TARGET_COUNT_SQUARE_SURFACE):
            target = self.targets[layout]["wallB"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "Back"
        for x in range(0, self.TARGET_COUNT_LONG_SURFACE):
            target = self.targets[layout]["wallL"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "Left"
        for x in range(0, self.TARGET_COUNT_LONG_SURFACE):
            target = self.targets[layout]["wallR"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "Right"
        for x in range(0, self.TARGET_COUNT_LONG_SURFACE):
            target = self.targets[layout]["ceiling"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "Ceiling"
        print "ERROR: Target not found among distractors. Poorly formed ini file."


    def getDistractorLocation(self, layout, wall, targetNo):
        location = None
        if wall.lower() == "front":
            location = self.targets[layout]['wallF'][targetNo][0]
        elif wall.lower() == "back":
            location = self.targets[layout]['wallB'][targetNo][0]
        elif wall.lower() == "left":
            location = self.targets[layout]['wallL'][targetNo][0]
        elif wall.lower() == "right":
            location = self.targets[layout]['wallR'][targetNo][0]
        elif wall.lower() == "ceiling":
            location = self.targets[layout]['ceiling'][targetNo][0]
        else:
            print "ERROR: Invalid wall name - \"" + wall + "\""
        return location

    def getDistractorIconImage(self, layout, wall, targetNo):
        icon = None
        if wall.lower() == "front":
            icon = self.targets[layout]['wallF'][targetNo][1]
        elif wall.lower() == "back":
            icon = self.targets[layout]['wallB'][targetNo][1]
        elif wall.lower() == "left":
            icon = self.targets[layout]['wallL'][targetNo][1]
        elif wall.lower() == "right":
            icon = self.targets[layout]['wallR'][targetNo][1]
        elif wall.lower() == "ceiling":
            icon = self.targets[layout]['ceiling'][targetNo][1]
        else:
            print "ERROR: Invalid wall name - \"" + wall + "\""
        return icon

client()
