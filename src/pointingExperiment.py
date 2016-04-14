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
import datetime


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
    USERNO = 0
    AGE = 0
    GENDER = 'M'
    SEQUENCENO = 0
    FRONTCANVASPROJ = 2
    RIGHTCANVASPROJ = 1
    BACKCANVASPROJ = 1
    LEFTCANVASPROJ = 1
    CEILINGCANVASPROJ = 1
    parallelTask = True
    wallToPlaneIndex = {'front': 0, 'right': 1, 'back': 2, 'left': 3, 'ceiling': 4}
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
    wallTargets = [[],[],[],[],[]]
    mouseLocationProp = (0,0)
    mouseProjector = 1
    mouseSurface = 1
    surfaceToCanvas = {}
    visibleTargets = []
    ceilingLength = 0
    floorLength = 0
    leftLength = 0
    rightLength = 0
    roomWidth = 0
    roomHeight = 0
    roomDepth = 0
    keyHit = False
    targetHit = False
    state = 0


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
                        elapsedSecs = (lClickRelTime - self.lClickTime).total_seconds()  # Checks how long the button was depressed
                        if (elapsedSecs < 0.15):
                            if self.state == 1:
                                if self.isKeyHit():
                                    self.keyHit = True
                            if self.state == 2:
                                if self.isTargetHit(self.currentLayout):
                                    self.targetHit = True
                        else:
                            pass
                    # Runs if the middle mouse button has been released
                    if (event.button == 2):
                        mClickRelTime = datetime.datetime.now()
                        elapsedSecs = (mClickRelTime - self.mClickTime).total_seconds()  # Checks how long the button was depressed
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
                        intersections = [1, 1, 1, 1, 1]
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
                                surfaces = ["front", "right", "back", "left", "ceiling"]
                                if (0 <= hProp <= 1) and (0 <= vProp <= 1) and hvecangle <= 90 and vvecangle <= 90:
                                    mouseLocations.append((hProp, vProp, self.wall2ProjectorSurface[surfaces[x]]))
                                else:
                                    intersections[x] = 0
                        #  NOTE - Secondary cursors are now never used but still exist just in case
                        x = 0  # This makes the ceiling always low priority and priority of walls is in clockwise order
                        if mouseLocations[x][2][0]==1:  # If the cursor is on projector 1
                            self.sender.hideCursor(2, self.curs[2])  # Hide cursors on other projector
                            self.sender.hideCursor(2, self.curs[3])  # Hide cursors on other projector
                            self.sender.hideCursor(1, self.curs[1])  # Hide other cursor on current projector
                            self.sender.relocateCursor(1, self.curs[0+x], mouseLocations[x][0], 1.0-mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                            self.mouseLocationProp = (mouseLocations[x][0], 1.0-mouseLocations[x][1])
                            self.mouseProjector = 1
                            self.mouseSurface = mouseLocations[x][2][1]
                            self.sender.showCursor(1, self.curs[0+x])
                        elif mouseLocations[x][2][0]==2:  # If the cursor is on projector 2
                            self.sender.hideCursor(1, self.curs[0])  # Hide cursors on other projector
                            self.sender.hideCursor(1, self.curs[1])  # Hide cursors on other projector
                            self.sender.hideCursor(2, self.curs[3])  # Hide other cursor on current projector
                            self.sender.relocateCursor(2, self.curs[2+x], mouseLocations[x][0], 1.0-mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                            self.mouseLocationProp = (mouseLocations[x][0], 1.0-mouseLocations[x][1])
                            self.mouseProjector = 2
                            self.mouseSurface = mouseLocations[x][2][1]
                            self.sender.showCursor(2, self.curs[2+x])
                else: # Runs if it is pointing that is to control the cursor
                    intersections = [1, 1, 1, 1, 1]
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
                            surfaces = ["front", "right", "back", "left", "ceiling"]
                            if (0 <= hProp <= 1) and (0 <= vProp <= 1) and hvecangle <= 90 and vvecangle <= 90:
                                mouseLocations.append((hProp, vProp, self.wall2ProjectorSurface[surfaces[x]]))
                            else:
                                intersections[x] = 0
                    # NOTE - Secondary cursors are now never used but still exist just in case
                    x = 0  # This makes the ceiling always low priority and priority of walls is in clockwise order
                    if mouseLocations[x][2][0] == 1:  # If the cursor is on projector 1
                        self.sender.hideCursor(2, self.curs[2])  # Hide cursors on other projector
                        self.sender.hideCursor(2, self.curs[3])  # Hide cursors on other projector
                        self.sender.hideCursor(1, self.curs[1])  # Hide other cursor on current projector
                        self.sender.relocateCursor(1, self.curs[0 + x], mouseLocations[x][0], 1.0 - mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                        self.mouseLocationProp = (mouseLocations[x][0], 1.0 - mouseLocations[x][1])
                        self.mouseProjector = 1
                        self.mouseSurface = mouseLocations[x][2][1]
                        self.sender.showCursor(1, self.curs[0 + x])
                    elif mouseLocations[x][2][0] == 2:  # If the cursor is on projector 2
                        self.sender.hideCursor(1, self.curs[0])  # Hide cursors on other projector
                        self.sender.hideCursor(1, self.curs[1])  # Hide cursors on other projector
                        self.sender.hideCursor(2, self.curs[3])  # Hide other cursor on current projector
                        self.sender.relocateCursor(2, self.curs[2 + x], mouseLocations[x][0], 1.0 - mouseLocations[x][1], "prop", mouseLocations[x][2][1])
                        self.mouseLocationProp = (mouseLocations[x][0], 1.0 - mouseLocations[x][1])
                        self.mouseProjector = 2
                        self.mouseSurface = mouseLocations[x][2][1]
                        self.sender.showCursor(2, self.curs[2 + x])

    # Locks the mouse so that the server can be controlled
    def LockMouse(self):
        self.mouseLock = True
        pygame.mouse.set_visible(False)
        self.sender.showCursor(1, self.curs[0])

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

    def drawTarget(self, wall, x, y, icon):
        projector, canvas = self.wallToProjCanvas(wall)
        targetDim = self.targets.getTargetDimensionProp(wall, self.roomHeight, self.roomWidth, self.roomDepth)
        target = self.sender.newTexRectangle(projector, canvas, x - (targetDim[0]/2), y + (targetDim[1]/2), targetDim[0], targetDim[1], "prop", "img/" + str(icon))
        self.visibleTargets.append((projector, target, canvas))
        return target

    def drawKeyBorder(self, wall, layout):
        projector, canvas = self.wallToProjCanvas(wall)
        targetDim = self.targets.getTargetDimensionProp(wall, self.roomHeight, self.roomWidth, self.roomDepth)
        x, y = self.targets.getTargetKeyLocationProp()
        targetDim = [targetDim[0]/75*100, targetDim[1]/75*100]
        self.border = (projector, self.sender.newRectangle(projector, canvas, x - (targetDim[0]/2), y + (targetDim[1]/2), targetDim[0], targetDim[1], "prop", (1, 0, 0, 1), 5, (0, 0, 0, 1)), canvas)

    def drawKeyLayout(self, layoutNo):
        targetIcon = self.targets.getTargetIcon(layoutNo)
        keyLocation = self.targets.getTargetKeyLocationProp()
        self.drawKeyBorder("Front", layoutNo)
        self.drawTarget("Front", keyLocation[0], keyLocation[1], targetIcon)

    def drawTargetLayout(self, layoutNo):
        for x in range(0, self.targets.getTargetCountSquareSurface()):
            distractorIcon = self.targets.getDistractorIcon(layoutNo, "Front", x)
            distractorLocation = self.targets.getDistractorLocationProp(layoutNo, "Front", x)
            self.drawTarget("Front", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets.getTargetCountSquareSurface()):
            distractorIcon = self.targets.getDistractorIcon(layoutNo, "Back", x)
            distractorLocation = self.targets.getDistractorLocationProp(layoutNo, "Back", x)
            self.drawTarget("Back", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets.getTargetCountLongSurface()):
            distractorIcon = self.targets.getDistractorIcon(layoutNo, "Left", x)
            distractorLocation = self.targets.getDistractorLocationProp(layoutNo, "Left", x)
            self.drawTarget("Left", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets.getTargetCountLongSurface()):
            distractorIcon = self.targets.getDistractorIcon(layoutNo, "Right", x)
            distractorLocation = self.targets.getDistractorLocationProp(layoutNo, "Right", x)
            self.drawTarget("Right", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets.getTargetCountLongSurface()):
            distractorIcon = self.targets.getDistractorIcon(layoutNo, "Ceiling", x)
            distractorLocation = self.targets.getDistractorLocationProp(layoutNo, "Ceiling", x)
            self.drawTarget("Ceiling", distractorLocation[0], distractorLocation[1], distractorIcon)

    def isTargetHit(self, layout):
        mouseCanvas = self.surfaceToCanvas[(self.mouseProjector, self.mouseSurface)]
        wallName = self.projCanvasToWall(self.mouseProjector, mouseCanvas[1]).lower()
        if wallName == self.targets.getTargetLocation(layout)[1].lower(): # Check whether mouse and target on same wall
            targetLocationProp = self.targets.getTargetLocationProp(layout)
            targetDim = self.targets.getTargetDimensionProp(wallName, self.roomHeight, self.roomWidth, self.roomDepth)
            xLeftTarget = targetLocationProp[0][0] - (targetDim[0]/2)
            xRightTarget = targetLocationProp[0][0] + (targetDim[0]/2)
            yTopTarget = targetLocationProp[0][1] + (targetDim[1]/2)
            yBottomTarget = targetLocationProp[0][1] - (targetDim[1]/2)
            if(self.mouseLocationProp[0]>=xLeftTarget and self.mouseLocationProp[0]<=xRightTarget):
                if(self.mouseLocationProp[1]>=yBottomTarget and self.mouseLocationProp[1]<=yTopTarget):
                    return True
        return False

    def isKeyHit(self):
        mouseCanvas = self.surfaceToCanvas[(self.mouseProjector, self.mouseSurface)]
        wallName = self.projCanvasToWall(self.mouseProjector, mouseCanvas[1]).lower()
        if wallName.lower() == "front":
            keyLocationProp = self.targets.getTargetKeyLocationProp()
            targetDim = self.targets.getTargetDimensionProp("front", self.roomHeight, self.roomWidth, self.roomDepth)
            targetDim = targetDim[0]/75*100, targetDim[1]/75*100
            xLeftTarget = keyLocationProp[0] - (targetDim[0] / 2)
            xRightTarget = keyLocationProp[0] + (targetDim[0] / 2)
            yTopTarget = keyLocationProp[1] + (targetDim[1] / 2)
            yBottomTarget = keyLocationProp[1] - (targetDim[1] / 2)
            if (self.mouseLocationProp[0] >= xLeftTarget and self.mouseLocationProp[0] <= xRightTarget):
                if (self.mouseLocationProp[1] >= yBottomTarget and self.mouseLocationProp[1] <= yTopTarget):
                    return True
        return False

    #self.angleBetweenVectors
    # Give grid coordinates and walls of start and end points to compute rotational distance between edges of start point and end point
    def getRotationalDists(self, layout):
        start, target = self.getStartAndTargetLocs(layout)
        headLoc = self.getHeadAxes()[0]
        startVec = start-headLoc
        targetVec = target-headLoc
        return self.angleBetweenVectors(startVec, targetVec)

    #return horizontal and vertical distances separately
    def getPlanarDists(self, layout):
        startX, startY = self.targets.getTargetKeyLocationProp()
        targetLoc, targetWall = self.targets.getTargetLocationProp(layout)
        targetGridX, targetGridY = targetLoc
        if(targetWall.lower() != "back"):
            if(targetWall.lower == "ceiling"):
                part1 = self.getSurfaceWidthRemUp(startX, startY, "front")
                part2 = self.getSurfaceWidthRemDown(targetGridX, targetGridY, "ceiling")
            elif(targetWall == "left"):
                part1 = self.getSurfaceWidthRemLeft(startX, startY, "front")
                part2 = self.getSurfaceWidthRemRight(targetGridX, targetGridY, "left")
            elif(targetWall == "right"):
                part1 = self.getSurfaceWidthRemRight(startX, startY, "front")
                part2 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY, "right")
            else:
                print "Invalid target wall"
        else:
            #Calculate distance across ceiling
            part1 = self.getSurfaceWidthRemUp(startX, startX, "front")
            part2 = self.getSurfaceLength("ceiling")
            part3 = self.getSurfaceWidthRemUp(targetGridX, targetGridY, "back")
            distanceCeiling = part1 + part2 + part3

            #Calculate distance across floor
            part1 = self.getSurfaceWidthRemDown(startX, startX, "front")
            part2 = self.getSurfaceLength("floor")
            part3 = self.getSurfaceWidthRemDown(targetGridX, targetGridY, "back")
            distanceFloor = part1 + part2 + part3

            #Calculate distance across left wall
            part1 = self.getSurfaceWidthRemLeft(startX, startX, "front")
            part2 = self.getSurfaceLength("left")
            part3 = self.getSurfaceWidthRemRight(targetGridX, targetGridY, "back")
            distanceLeft = part1 + part2 + part3

            #Calculate distance across right wall
            part1 = self.getSurfaceWidthRemRight(startX, startX, "front")
            part2 = self.getSurfaceLength("right")
            part3 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY, "back")
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

    def getSurfaceLength(self, wall):
        if wall.lower() == "ceiling":
            return self.ceilingLength
        elif wall.lower() == "left":
            return self.leftLength
        elif wall.lower() == "right":
            return self.rightLength
        elif wall.lower() == "floor":
            return self.floorLength
        else:
            print "Invalid surface name - " + str(wall)
            return 0

    def getDirectDists(self, layout):
        start, target = self.getStartAndTargetLocs(layout)
        return self.distBetweenPoints(start, target)

    def getSurfaceWidthRemLeft(self, realPointX, realPointY, wall):
        wall = self.wallToPlaneIndex[wall.lower()]
        realEdgeX, realEdgeY = 0, realPointY
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

    def getSurfaceWidthRemRight(self, realPointX, realPointY, wall):
        wall = self.wallToPlaneIndex[wall.lower()]
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

    def getSurfaceWidthRemUp(self, realPointX, realPointY, wall):
        wall = self.wallToPlaneIndex[wall.lower()]
        realEdgeX, realEdgeY = realPointX, 1
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

    def getSurfaceWidthRemDown(self, realPointX, realPointY, wall):
        wall = self.wallToPlaneIndex[wall.lower()]
        realEdgeX, realEdgeY = realPointX, 0
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
    def getStartAndTargetLocs(self, layout):
        realStartX, realStartY = self.targets.getTargetKeyLocationProp()
        targetLoc, targetWall = self.targets.getTargetLocationProp(layout)
        realTargetX, realTargetY = targetLoc
        startWall = self.wallToPlaneIndex["front"]
        targetWall = self.wallToPlaneIndex[targetWall.lower()]
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

    def clearTargetLayout(self):
        for x in range(0, len(self.visibleTargets)):
            projector, elementNo, canvasNo = self.visibleTargets[x]
            self.sender.removeElement(projector, elementNo, canvasNo)
            self.sender.removeElement(self.border[0], self.border[1], self.border[2])

    # Sets up the surfaces which can be defined within the client
    def initGUI(self):
        self.wallCanvases = []
        self.wallCanvases.append((self.FRONTCANVASPROJ, self.sender.newCanvas(self.FRONTCANVASPROJ, 1, 0, 1, 1, 1, "prop", "front")))
        self.wallCanvases.append((self.RIGHTCANVASPROJ, self.sender.newCanvas(self.RIGHTCANVASPROJ, 1, 0, 1, 1, 1, "prop", "right")))
        self.wallCanvases.append((self.BACKCANVASPROJ, self.sender.newCanvas(self.BACKCANVASPROJ, 2, 0, 1, 1, 1, "prop", "back")))
        self.wallCanvases.append((self.LEFTCANVASPROJ, self.sender.newCanvas(self.LEFTCANVASPROJ, 3, 0, 1, 1, 1, "prop", "left")))
        self.wallCanvases.append((self.CEILINGCANVASPROJ, self.sender.newCanvas(self.CEILINGCANVASPROJ, 4, 0, 1, 1, 1, "prop", "ceiling")))
        self.surfaceToCanvas[(self.FRONTCANVASPROJ, 1)] = self.wallCanvases[0]
        self.surfaceToCanvas[(self.RIGHTCANVASPROJ, 1)] = self.wallCanvases[1]
        self.surfaceToCanvas[(self.BACKCANVASPROJ, 2)] = self.wallCanvases[2]
        self.surfaceToCanvas[(self.LEFTCANVASPROJ, 3)] = self.wallCanvases[3]
        self.surfaceToCanvas[(self.CEILINGCANVASPROJ, 4)] = self.wallCanvases[4]
        self.curs = []
        self.curs.append(self.sender.newCursor(1, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(1, self.curs[0])
        self.curs.append(self.sender.newCursor(1, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(1, self.curs[1])
        self.curs.append(self.sender.newCursor(2, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(2, self.curs[0])
        self.curs.append(self.sender.newCursor(2, 1, 0.5, 0.5, "prop"))
        self.sender.hideCursor(2, self.curs[1])

    def wallToProjCanvas(self, wall):
        for x in range(0, len(self.wallCanvases)):
            if self.sender.getCanvasName(self.wallCanvases[x][0], self.wallCanvases[x][1]) == wall.lower():
                return self.wallCanvases[x][0], self.wallCanvases[x][1]
        print "No such wall"
        return None

    def projCanvasToWall(self, projector, canvas):
        for x in range(0, len(self.wallCanvases)):
            if self.wallCanvases[x][0] == projector and self.wallCanvases[x][1] == canvas:
                return self.sender.getCanvasName(self.wallCanvases[x][0], self.wallCanvases[x][1])
        print "No such projector/canvas combination: proj = " + str(projector) + ", canvas = " + str(canvas)
        return None


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

            self.ceilingLength = (self.distBetweenPoints(content[26], content[29]) + self.distBetweenPoints(content[27], content[28]))/2
            self.floorLength = (self.distBetweenPoints(content[4], content[17]) + self.distBetweenPoints(content[5], content[16]))/2
            self.rightLength = (self.distBetweenPoints(content[8], content[9]) + self.distBetweenPoints(content[11], content[10]))/2
            self.leftLength = (self.distBetweenPoints(content[20], content[21]) + self.distBetweenPoints(content[23], content[22]))/2
            self.roomDepth = (self.ceilingLength + self.floorLength + self.leftLength + self.rightLength)/4

            ceilingWidth = (self.distBetweenPoints(content[26], content[27]) + self.distBetweenPoints(content[29], content[28]))/2
            leftHeight = (self.distBetweenPoints(content[21], content[22]) + self.distBetweenPoints(content[23], content[20]))/2
            rightHeight = (self.distBetweenPoints(content[9], content[10]) + self.distBetweenPoints(content[11], content[8]))/2
            floorWidth = (self.distBetweenPoints(content[4], content[5]) + self.distBetweenPoints(content[17], content[16]))/2
            frontWidth = (self.distBetweenPoints(content[2], content[3]) + self.distBetweenPoints(content[5], content[4]))/2
            frontHeight = (self.distBetweenPoints(content[2], content[5]) + self.distBetweenPoints(content[4], content[3]))/2
            backWidth = (self.distBetweenPoints(content[14], content[15]) + self.distBetweenPoints(content[17], content[16]))/2
            backHeight = (self.distBetweenPoints(content[14], content[17]) + self.distBetweenPoints(content[16], content[15]))/2

            self.roomWidth = (frontWidth + backWidth + ceilingWidth + floorWidth)/4
            self.roomHeight = (frontHeight + leftHeight + rightHeight + backHeight)/4

    def loadOrderFile(self, filename):


    # The main loop
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        temp = parser.get('RoomSetup', 'frontSurface')
        temp = temp.split(";")
        self.wall2ProjectorSurface["front"] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'rightSurface')
        temp = temp.split(";")
        self.wall2ProjectorSurface["right"] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'backSurface')
        temp = temp.split(";")
        self.wall2ProjectorSurface["back"] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'leftSurface')
        temp = temp.split(";")
        self.wall2ProjectorSurface["left"] = (int(temp[0]), int(temp[1]))
        temp = parser.get('RoomSetup', 'ceilingSurface')
        temp = temp.split(";")
        self.wall2ProjectorSurface["ceiling"] = (int(temp[0]), int(temp[1]))
        self.targets = Targets()
        self.targets.parseFile("targets.ini")


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
        self.state = 0

        self.mouseLock = False
        pygame.mouse.set_visible(False)

        mouseThread = threading.Thread(target=self.mouseMovement, args=())  # Creates the display thread
        mouseThread.start()  # Starts the display thread
        self.currentLayout = 1
        now = datetime.datetime.now()

        order = {}
        with open("order1.csv") as f:
            records = csv.DictReader(f)
            for row in records:
                order[row['layout']] = row
        orderIndex = 1

        with open(str(self.USERNO) + "_trialDetails.csv", 'w') as trialDetailsCSV:
            fieldnames = ['user_number',
                          'date',
                          'time',
                          'age',
                          'gender',
                          'sequence_number',
                          'room_width',
                          'room_height',
                          'room_depth',
                          'key_location_prop',
                          'target_dim_prop_F_B',
                          'target_dim_prop_L_R',
                          'target_dim_prop_C']
            writer = csv.DictWriter(trialDetailsCSV, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'user_number': str(self.USERNO),
                             'date': str(now.date().day).zfill(2) + "/" +
                                     str(now.date().month).zfill(2) + "/" +
                                     str(now.date().year),
                             'time': str(now.time().hour).zfill(2) + ":" +
                                     str(now.time().minute).zfill(2) + ":" +
                                     str(now.time().second).zfill(2),
                             'age': str(self.AGE),
                             'gender': self.GENDER,
                             'sequence_number': str(self.SEQUENCENO),
                             'room_width': str(self.roomWidth),
                             'room_height': str(self.roomHeight),
                             'room_depth': str(self.roomDepth),
                             'key_location_prop': str(self.targets.getTargetKeyLocationProp()[0]) + "," +
                                             str(self.targets.getTargetKeyLocationProp()[1]),
                             'target_dim_prop_F_B': str(self.targets.getTargetDimensionProp('front', self.roomHeight, self.roomWidth, self.roomDepth)[0]) + "," +
                                               str(self.targets.getTargetDimensionProp('front', self.roomHeight, self.roomWidth, self.roomDepth)[1]),
                             'target_dim_prop_L_R': str(self.targets.getTargetDimensionProp('left', self.roomHeight, self.roomWidth, self.roomDepth)[0]) + "," +
                                               str(self.targets.getTargetDimensionProp('left', self.roomHeight, self.roomWidth, self.roomDepth)[1]),
                             'target_dim_prop_C': str(self.targets.getTargetDimensionProp('ceiling', self.roomHeight, self.roomWidth, self.roomDepth)[0]) + "," +
                                               str(self.targets.getTargetDimensionProp('ceiling', self.roomHeight, self.roomWidth, self.roomDepth)[1])})

        with open(str(self.USERNO) + "_trialResults.csv", 'w') as trialDetailsCSV:
            fieldnames = ['condition1',  # pointing vs perspective
                          'condition2',  # Synchronous vs asychronous
                          'target_ini',
                          'target_layout',
                          'no_distractors_long',
                          'no_distractors_square',
                          'trial_num_exp',
                          'trial_num_cond',
                          'direct_dist',
                          'angular_dist',
                          'surface_dist',
                          'trace_file',
                          'trace_distance',
                          'target_icon',
                          'target_location',
                          'depth_icons',
                          'width_icons',
                          'height_icons',
                          'icon_width',
                          'trial_time',
                          'trial_date',
                          'head_coordinates',  # For perspective
                          'tracker_coordinates',  # For pointing
                          'finding_duration',  # For asynchronous
                          'moving_duration',
                          'max_mouse_velocity',
                          'no_walls_passed',
                          'no_walls_needed',
                          'integrality',
                          'seperability'
                          ]
            writer = csv.DictWriter(trialDetailsCSV, fieldnames=fieldnames)
            writer.writeheader()
            self.loadOrderFile()

            if (self.quit == False):
                while (self.quit == False):
                    self.background.fill((255, 255, 255))
                    text = self.font.render("", 1, (10, 10, 10))
                    textpos = text.get_rect()
                    textpos.centerx = self.background.get_rect().centerx
                    self.background.blit(text, textpos)
                    self.getInput(False)

                    # Run experimental process
                    if self.state == 0:
                        self.drawKeyLayout(self.currentLayout)
                        if not self.parallelTask:
                            self.drawTargetLayout(self.currentLayout)
                        self.state = 1
                        self.keyHit = False
                    elif self.state == 1:
                        if self.keyHit:
                            if self.parallelTask:
                                self.drawTargetLayout(self.currentLayout)
                            self.sender.setRectangleLineColor(self.border[0], self.border[1], (0, 1, 0, 1))
                            self.keyClickTime = datetime.datetime.now()
                            self.state = 2
                            self.targetHit = False
                    elif self.state == 2:
                        if self.targetHit:
                            self.targetClickTime = datetime.datetime.now()
                            elapsedSecs = (self.targetClickTime - self.keyClickTime).total_seconds()
                            headLoc = self.getHeadAxes()[0]
                            trackerLoc = self.getTrackerData()[0][0]
                            writer.writerow({'condition1': self.CONDITION1,  # pointing vs perspective
                                             'condition2': self.CONDITION2,  # Synchronous vs asychronous
                                             'target_ini': self.TARGETINI,
                                             'target_layout': self.currentLayout,
                                             'no_distractors_long': self.targets[self.CONDITION1, self.CONDITION2].getTargetCountLongSurface(),
                                             'no_distractors_square': self.targets[self.CONDITION1, self.CONDITION2].getTargetCountSquareSurface(),
                                             'trial_num_cond': self.getTrialNumCond(self.CONDITION1, self.CONDITION2),
                                             'direct_dist': self.getDirectDists(self.currentLayout),
                                             'angular_dist': self.getRotationalDists(self.currentLayout),
                                             'surface_dist': self.getPlanarDists(self.currentLayout),
                                             'trace_file': str(self.getTrialNumCond(self.CONDITION1, self.CONDITION2)) + "_" + self.CONDITION1 + "_" + self.CONDITION2 + ".csv" ,
                                             'trace_distance': str(traceDistance),
                                             'target_icon': self.targets[self.CONDITION1, self.CONDITION2].getTargetIcon(self.currentLayout),
                                             'target_location': self.targets[self.CONDITION1, self.CONDITION2].getTargetLocationProp(self.currentLayout),
                                             'depth_icons': self.targets[self.CONDITION1, self.CONDITION2].getTargetsDeep(),
                                             'width_icons': self.targets[self.CONDITION1, self.CONDITION2].getTargetsWide(),
                                             'height_icons': self.targets[self.CONDITION1, self.CONDITION2].getTargetsTall(),
                                             'trial_time': str(now.time().hour).zfill(2) + ":" +
                                                           str(now.time().minute).zfill(2) + ":" +
                                                           str(now.time().second).zfill(2),
                                             'trial_date': str(now.date().day).zfill(2) + "/" +
                                                           str(now.date().month).zfill(2) + "/" +
                                                           str(now.date().year),
                                             'head_coordinates': str(headLoc[0]) + "," +
                                                                 str(headLoc[1]),  # For perspective
                                             'tracker_coordinates': str(trackerLoc[0]) + "," +
                                                                    str(trackerLoc[1]),  # For pointing
                                             'finding_duration': sfsdf,  # For asynchronous
                                             'moving_duration': elapsedSecs,
                                             'max_mouse_velocity': self.maxMouseVelocity,
                                             'no_walls_passed': self.passedWalls,
                                             'no_walls_needed': self.neededWalls,
                                             'euc_to_city_block': self.ratio})
                            self.incrementTrialNumCond(self.CONDITION1, self.CONDITION2)
                            print "Time elapsed: " + str(elapsedSecs)  # TODO Record to file instead of printing
                            self.clearTargetLayout()
                            self.currentLayout += 1  #TODO Make order file which contains target ini file name and layout numbers use this as index to that
                            self.state = 0

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
    targetDimProp = None

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
        self.targetAreaTall = 1.0/self.NO_TARGETS_TALL
        self.targetAreaWide = 1.0/self.NO_TARGETS_WIDE
        self.targetAreaDepth = 1.0/self.NO_TARGETS_DEEP

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

    def getTargetKeyLocationProp(self):
        gridLoc = self.getTargetKeyLocation()
        widthSegment = 1.0/self.getTargetsWide()
        locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
        heightSegment = 1.0/self.getTargetsTall()
        locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        return locationX, locationY

    def getTargetIcon(self, layout):
        return self.targets[layout]['target']

    def getTargetDimensionProp(self, wall, realRoomHeight, realRoomWidth, realRoomDepth):
        realTargetAreaTall = self.targetAreaTall * realRoomHeight
        realTargetAreaWide = self.targetAreaWide * realRoomWidth
        realTargetAreaDeep = self.targetAreaDepth * realRoomDepth
        realTargetDeepProp = 0
        realTargetWideProp = 0
        realTargetTallProp = 0
        if realTargetAreaTall <= realTargetAreaWide and realTargetAreaTall <= realTargetAreaDeep:
            realTargetTallReal = 0.75 * realTargetAreaTall
            realTargetTallProp = 0.75 * self.targetAreaTall
            realTargetWideProp = realTargetTallReal/realRoomWidth
            realTargetDeepProp = realTargetTallReal/realRoomDepth
        elif realTargetAreaWide <= realTargetAreaTall and realTargetAreaWide <= realTargetAreaDeep:
            realTargetWideReal = 0.75 * realTargetAreaWide
            realTargetWideProp = 0.75 * self.targetAreaWide
            realTargetTallProp = realTargetWideReal/realRoomHeight
            realTargetDeepProp = realTargetWideReal/realRoomDepth
        elif realTargetAreaDeep <= realTargetAreaTall and realTargetAreaDeep <= realTargetAreaWide:
            realTargetDeepReal = 0.75 * realTargetAreaDeep
            realTargetDeepProp = 0.75 * self.targetAreaDepth
            realTargetWideProp = realTargetDeepReal/realRoomWidth
            realTargetTallProp = realTargetDeepReal/realRoomHeight
        if wall.lower() == "front" or wall.lower() == "back":
            return (realTargetWideProp, realTargetTallProp)
        elif wall.lower() == "left" or wall.lower() == "right":
            return (realTargetDeepProp, realTargetTallProp)
        elif wall.lower() == "ceiling":
            return (realTargetWideProp, realTargetDeepProp)
        print "ERROR: Invalid wall name \"" + str(wall) + "\""
        return 0, 0

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

    def getTargetLocationProp(self, layout):
        gridLoc = self.getTargetLocation(layout)
        locationX = 0
        locationY = 0
        wall = gridLoc[1]
        gridLoc = gridLoc[0]
        if wall.lower() == "front" or wall.lower() == "back":
            widthSegment = 1.0/self.getTargetsWide()
            locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
            heightSegment = 1.0/self.getTargetsTall()
            locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        elif wall.lower() == "left" or wall.lower() == "right":
            widthSegment = 1.0/self.getTargetsDeep()
            locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
            heightSegment = 1.0/self.getTargetsTall()
            locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        elif wall.lower() == "ceiling":
            widthSegment = 1.0/self.getTargetsWide()
            locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
            heightSegment = 1.0/self.getTargetsDeep()
            locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        return (locationX, locationY), wall

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

    def getDistractorLocationProp(self, layout, wall, targetNo):
        gridLoc = self.getDistractorLocation(layout, wall, targetNo)
        locationX = 0
        locationY = 0
        if wall.lower() == "front" or wall.lower() == "back":
            widthSegment = 1.0/self.getTargetsWide()
            locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
            heightSegment = 1.0/self.getTargetsTall()
            locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        elif wall.lower() == "left" or wall.lower() == "right":
            widthSegment = 1.0/self.getTargetsDeep()
            locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
            heightSegment = 1.0/self.getTargetsTall()
            locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        elif wall.lower() == "ceiling":
            widthSegment = 1.0/self.getTargetsWide()
            locationX = (widthSegment*gridLoc[0])-(widthSegment/2)
            heightSegment = 1.0/self.getTargetsDeep()
            locationY = (heightSegment*gridLoc[1])-(heightSegment/2)
        return locationX, locationY

    def getDistractorIcon(self, layout, wall, targetNo):
        icon = None
        if wall.lower() == "front":
            icon = self.targets[layout]['wallF'][targetNo][1]
            print "Showing front icon " + icon
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
