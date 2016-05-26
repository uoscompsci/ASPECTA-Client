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
import os.path
import os, glob


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
    recordPath = False
    passedSurfaces = 0
    conditionCounter = {"pointing,synchronous": 0, "perspective,synchronous": 0,
                        "pointing,asynchronous": 0, "perspective,asynchronous": 0}
    alreadyPassed = ["front"]


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
                            if self.state == 0.5:
                                self.foundClick = True
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
        startTime = datetime.datetime.now()
        segCheck2 = self.getTrackerData()[0][0]
        segCheck3 = self.getTrackerData()[0][1]
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
                                vVec = self.planes[x][7] - self.planes[x][2]
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
                                surfaces = ["front", "right", "back", "left", "ceiling", "floor"]
                                isWallChange = False
                                if (0 <= hProp <= 1) and (0 <= vProp <= 1) and hvecangle <= 90 and vvecangle <= 90:
                                    mouseLocations.append((hProp, vProp, self.wall2ProjectorSurface[surfaces[x]]))
                                    if len(mouseLocations) == 1 and self.state == 2:
                                        if surfaces[x]!=self.currentSurface:
                                            if surfaces[x] not in self.alreadyPassed:
                                                self.passedSurfaces += 1
                                                self.alreadyPassed.append(surfaces[x])
                                            self.currentSurface = surfaces[x]
                                            isWallChange = True
                                else:
                                    intersections[x] = 0
                                temptime = datetime.datetime.now()
                                if self.state==2:
                                    moveDuration = (temptime-startTime).total_seconds()
                                    startTime = temptime
                                    distance = self.distBetweenPoints(self.intersect, oldIntersect)
                                    angle = self.angleBetweenVectors(self.intersect-lastHeadLoc, oldIntersect-lastHeadLoc)
                                    degreesPerSecond = 0
                                    distanceUnitsPerSecond = 0
                                    if not isWallChange:
                                        degreesPerSecond = angle/moveDuration
                                        distanceUnitsPerSecond = distance/moveDuration
                                    self.currentPath.append({"userLoc": lastHeadLoc, "startPoint": oldIntersect,
                                                             "endPoint": self.intersect, "distance": distance,
                                                             "angle": angle, "angularVelocity": degreesPerSecond,
                                                             "velocity": distanceUnitsPerSecond,
                                                             "time": str(temptime.time().hour).zfill(2) +
                                                                     ":" + str(temptime.time().minute).zfill(2) +
                                                                     ":" + str(temptime.time().second).zfill(2)})

                        #  NOTE - Secondary cursors are now never used but still exist just in case
                        x = 0  # This makes the ceiling always low priority and priority of walls is in clockwise order
                        if len(mouseLocations)!=0:
                            if mouseLocations[x][2][0]==1:  # If the cursor is on projector 1
                                wall = self.projCanvasToWall(mouseLocations[x][2][0], mouseLocations[x][2][1])
                                if wall != "floor" and mouseLocations[x][1] < self.upperProjectionProp[wall]:
                                    self.sender.hideCursor(2, self.curs[2])  # Hide cursors on other projector
                                    self.sender.hideCursor(2, self.curs[3])  # Hide cursors on other projector
                                    self.sender.hideCursor(1, self.curs[1])  # Hide other cursor on current projector
                                    self.sender.relocateCursor(1, self.curs[0 + x], mouseLocations[x][0], 1.0-mouseLocations[x][1]/self.upperProjectionProp[wall], "prop", mouseLocations[x][2][1])
                                    self.mouseLocationProp = (mouseLocations[x][0], 1.0-mouseLocations[x][1]/self.upperProjectionProp[wall])
                                    self.mouseProjector = 1
                                    self.mouseSurface = mouseLocations[x][2][1]
                                    self.sender.showCursor(1, self.curs[0 + x])
                                else:
                                    self.sender.hideCursor(2, self.curs[2])
                                    self.sender.hideCursor(2, self.curs[3])
                                    self.sender.hideCursor(1, self.curs[0])
                                    self.sender.hideCursor(1, self.curs[1])
                            elif mouseLocations[x][2][0]==2:  # If the cursor is on projector 2
                                wall = self.projCanvasToWall(mouseLocations[x][2][0], mouseLocations[x][2][1])
                                if wall != "floor" and mouseLocations[x][1] < self.upperProjectionProp[wall]:
                                    self.sender.hideCursor(1, self.curs[0])  # Hide cursors on other projector
                                    self.sender.hideCursor(1, self.curs[1])  # Hide cursors on other projector
                                    self.sender.hideCursor(2, self.curs[3])  # Hide other cursor on current projector
                                    self.sender.relocateCursor(2, self.curs[2+x], mouseLocations[x][0], 1.0-mouseLocations[x][1]/self.upperProjectionProp[wall], "prop", mouseLocations[x][2][1])
                                    self.mouseLocationProp = (mouseLocations[x][0], 1.0-mouseLocations[x][1]/self.upperProjectionProp[wall])
                                    self.mouseProjector = 2
                                    self.mouseSurface = mouseLocations[x][2][1]
                                    self.sender.showCursor(2, self.curs[2+x])
                                else:
                                    self.sender.hideCursor(2, self.curs[2])
                                    self.sender.hideCursor(2, self.curs[3])
                                    self.sender.hideCursor(1, self.curs[0])
                                    self.sender.hideCursor(1, self.curs[1])
                else: # Runs if it is pointing that is to control the cursor
                    for x in range(0, len(self.planes)):  # Finds where the last intersect point was
                        segCheck = self.segmentPlane(self.planes[x], segCheck2, segCheck3)
                        if(segCheck == 1):
                            break
                    oldIntersect = self.intersect  # Saves the last intersect point
                    axes = self.getHeadAxes()
                    lastHeadLoc = axes[0]  # From now on the current head location is used
                    pygame.mouse.set_pos([self.winWidth / 2, self.winHeight / 2])  # Returns cursor to the middle of the window
                    intersections = [1, 1, 1, 1, 1]
                    mouseLocations = []
                    for x in range(0, len(self.planes)):
                        segCheck2 = self.getTrackerData()[0][0]
                        segCheck3 = self.getTrackerData()[0][1]
                        segCheck = self.segmentPlane(self.planes[x], segCheck2, segCheck3)
                        if segCheck == 1:
                            intersections[x] = scipy.array([self.intersect[0], self.intersect[1], self.intersect[2]])
                            diagVec = intersections[x] - self.planes[x][2]
                            hVec = self.planes[x][3] - self.planes[x][2]
                            vVec = self.planes[x][7] - self.planes[x][2]
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
                            surfaces = ["front", "right", "back", "left", "ceiling", "floor"]
                            isWallChange = False
                            if (0 <= hProp <= 1) and (0 <= vProp <= 1) and hvecangle <= 90 and vvecangle <= 90:
                                mouseLocations.append((hProp, vProp, self.wall2ProjectorSurface[surfaces[x]]))
                                if len(mouseLocations) == 1 and self.state == 2:
                                    if surfaces[x] != self.currentSurface: #Current surface is what was last recorded as the current surfrace
                                        if surfaces[x] not in self.alreadyPassed:
                                            self.passedSurfaces += 1
                                            self.alreadyPassed.append(surfaces[x])
                                        self.currentSurface = surfaces[x] #What is this doing?
                                        isWallChange = True
                            else:
                                intersections[x] = 0
                            temptime = datetime.datetime.now()
                            if self.state == 2:
                                moveDuration = (temptime - startTime).total_seconds()
                                startTime = temptime
                                distance = self.distBetweenPoints(self.intersect, oldIntersect)
                                angle = self.angleBetweenVectors(self.intersect - lastHeadLoc,
                                                                 oldIntersect - lastHeadLoc) # TODO SHOULDN'T BE HEAD LOC
                                degreesPerSecond = 0
                                distanceUnitsPerSecond = 0
                                if not isWallChange and moveDuration != 0:
                                    degreesPerSecond = angle / moveDuration
                                    distanceUnitsPerSecond = distance / moveDuration
                                elif moveDuration == 0:
                                    degreesPerSecond = 0
                                    distanceUnitsPerSecond = 0
                                self.currentPath.append({"userLoc": lastHeadLoc, "startPoint": oldIntersect,
                                                         "endPoint": self.intersect, "distance": distance,
                                                         "angle": angle, "angularVelocity": degreesPerSecond,
                                                         "velocity": distanceUnitsPerSecond,
                                                         "time": str(temptime.time().hour).zfill(2) +
                                                                 ":" + str(temptime.time().minute).zfill(2) +
                                                                 ":" + str(temptime.time().second).zfill(2)})
                    # NOTE - Secondary cursors are now never used but still exist just in case
                    x = 0  # This makes the ceiling always low priority and priority of walls is in clockwise order
                    if len(mouseLocations)!=0:
                        if mouseLocations[x][2][0] == 1:  # If the cursor is on projector 1
                            wall = self.projCanvasToWall(mouseLocations[x][2][0], mouseLocations[x][2][1])
                            if wall != "floor" and mouseLocations[x][1] < self.upperProjectionProp[wall]:
                                self.sender.hideCursor(2, self.curs[2])  # Hide cursors on other projector
                                self.sender.hideCursor(2, self.curs[3])  # Hide cursors on other projector
                                self.sender.hideCursor(1, self.curs[1])  # Hide other cursor on current projector
                                self.sender.relocateCursor(1, self.curs[0 + x], mouseLocations[x][0], 1.0 - mouseLocations[x][1]/self.upperProjectionProp[wall], "prop", mouseLocations[x][2][1])
                                self.mouseLocationProp = (mouseLocations[x][0], 1.0 - mouseLocations[x][1]/self.upperProjectionProp[wall])
                                self.mouseProjector = 1
                                self.mouseSurface = mouseLocations[x][2][1]
                                self.sender.showCursor(1, self.curs[0 + x])
                            else:
                                self.sender.hideCursor(2, self.curs[2])
                                self.sender.hideCursor(2, self.curs[3])
                                self.sender.hideCursor(1, self.curs[0])
                                self.sender.hideCursor(1, self.curs[1])
                        elif mouseLocations[x][2][0] == 2:  # If the cursor is on projector 2
                            wall = self.projCanvasToWall(mouseLocations[x][2][0], mouseLocations[x][2][1])
                            if wall != "floor" and mouseLocations[x][1] < self.upperProjectionProp[wall]:
                                self.sender.hideCursor(1, self.curs[0])  # Hide cursors on other projector
                                self.sender.hideCursor(1, self.curs[1])  # Hide cursors on other projector
                                self.sender.hideCursor(2, self.curs[3])  # Hide other cursor on current projector
                                self.sender.relocateCursor(2, self.curs[2 + x], mouseLocations[x][0], 1.0 - mouseLocations[x][1]/self.upperProjectionProp[wall], "prop", mouseLocations[x][2][1])
                                self.mouseLocationProp = (mouseLocations[x][0], 1.0 - mouseLocations[x][1]/self.upperProjectionProp[wall])
                                self.mouseProjector = 2
                                self.mouseSurface = mouseLocations[x][2][1]
                                self.sender.showCursor(2, self.curs[2 + x])
                            else:
                                self.sender.hideCursor(2, self.curs[2])
                                self.sender.hideCursor(2, self.curs[3])
                                self.sender.hideCursor(1, self.curs[0])
                                self.sender.hideCursor(1, self.curs[1])

    def pathLength(self, path):
        totalLength = 0
        for x in range(1, len(path)): #The first is skipped because the "start" point was before recording
            totalLength += path[x]["distance"]
        return totalLength

    def pathAngle(self, path):
        totalAngle = 0
        for x in range(1, len(path)):  # The first is skipped because the "start" point was before recording
            totalAngle += path[x]["angle"]
        return totalAngle

    def fastestAngularVelocity(self, path):
        velocity = 0
        for x in range(1, len(path)):
            tempVelocity = path[x]["angularVelocity"]
            if tempVelocity>velocity:
                velocity = tempVelocity
        return velocity

    def fastestVelocity(self, path):
        velocity = 0
        for x in range(1, len(path)):
            tempVelocity = path[x]["velocity"]
            if tempVelocity>velocity:
                velocity = tempVelocity
        return velocity

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
        targetDim = self.targets[self.TARGETINI].getTargetDimensionProp(wall)
        target = self.sender.newTexRectangle(projector, canvas, x - (targetDim[0]/2), y + (targetDim[1]/2), targetDim[0], targetDim[1], "prop", "img/" + str(icon))
        self.visibleTargets.append((projector, target, canvas))
        return target

    def drawKeyBorder(self, wall, layout):
        projector, canvas = self.wallToProjCanvas(wall)
        targetDim = self.targets[self.TARGETINI].getTargetDimensionProp(wall)
        x, y = self.targets[self.TARGETINI].getTargetKeyLocationProp()
        targetDim = [targetDim[0]/75*100, targetDim[1]/75*100]
        self.border = (projector, self.sender.newRectangle(projector, canvas, x - (targetDim[0]/2), y + (targetDim[1]/2), targetDim[0], targetDim[1], "prop", (1, 0, 0, 1), 5, (0, 0, 0, 1)), canvas)

    def drawKeyLayout(self, layoutNo):
        targetIcon = self.targets[self.TARGETINI].getTargetIcon(layoutNo)
        keyLocation = self.targets[self.TARGETINI].getTargetKeyLocationProp()
        self.drawKeyBorder("front", layoutNo)
        self.drawTarget("front", keyLocation[0], keyLocation[1], targetIcon)

    def drawTargetLayout(self, layoutNo):
        for x in range(0, self.targets[self.TARGETINI].getTargetCountSquareSurface()):
            distractorIcon = self.targets[self.TARGETINI].getDistractorIcon(layoutNo, "front", x)
            distractorLocation = self.targets[self.TARGETINI].getDistractorLocationProp(layoutNo, "front", x)
            self.drawTarget("front", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets[self.TARGETINI].getTargetCountSquareSurface()):
            distractorIcon = self.targets[self.TARGETINI].getDistractorIcon(layoutNo, "back", x)
            distractorLocation = self.targets[self.TARGETINI].getDistractorLocationProp(layoutNo, "back", x)
            self.drawTarget("back", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets[self.TARGETINI].getTargetCountLongSurface()):
            distractorIcon = self.targets[self.TARGETINI].getDistractorIcon(layoutNo, "left", x)
            distractorLocation = self.targets[self.TARGETINI].getDistractorLocationProp(layoutNo, "left", x)
            self.drawTarget("left", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets[self.TARGETINI].getTargetCountLongSurface()):
            distractorIcon = self.targets[self.TARGETINI].getDistractorIcon(layoutNo, "right", x)
            distractorLocation = self.targets[self.TARGETINI].getDistractorLocationProp(layoutNo, "right", x)
            self.drawTarget("right", distractorLocation[0], distractorLocation[1], distractorIcon)

        for x in range(0, self.targets[self.TARGETINI].getTargetCountLongSurface()):
            distractorIcon = self.targets[self.TARGETINI].getDistractorIcon(layoutNo, "ceiling", x)
            distractorLocation = self.targets[self.TARGETINI].getDistractorLocationProp(layoutNo, "ceiling", x)
            self.drawTarget("ceiling", distractorLocation[0], distractorLocation[1], distractorIcon)

    def isTargetHit(self, layout):
        mouseCanvas = self.surfaceToCanvas[(self.mouseProjector, self.mouseSurface)]
        wallName = self.projCanvasToWall(self.mouseProjector, mouseCanvas[1]).lower()
        if wallName == self.targets[self.TARGETINI].getTargetLocation(layout)[1].lower(): # Check whether mouse and target on same wall
            targetLocationProp = self.targets[self.TARGETINI].getTargetLocationProp(layout)
            targetDim = self.targets[self.TARGETINI].getTargetDimensionProp(wallName)
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
            keyLocationProp = self.targets[self.TARGETINI].getTargetKeyLocationProp()
            targetDim = self.targets[self.TARGETINI].getTargetDimensionProp("front")
            targetDim = targetDim[0]/75*100, targetDim[1]/75*100
            xLeftTarget = keyLocationProp[0] - (targetDim[0] / 2)
            xRightTarget = keyLocationProp[0] + (targetDim[0] / 2)
            yTopTarget = keyLocationProp[1] + (targetDim[1] / 2)
            yBottomTarget = keyLocationProp[1] - (targetDim[1] / 2)
            if (self.mouseLocationProp[0] >= xLeftTarget and self.mouseLocationProp[0] <= xRightTarget):
                if (self.mouseLocationProp[1] >= yBottomTarget and self.mouseLocationProp[1] <= yTopTarget):
                    return True
        return False

    # Give grid coordinates and walls of start and end points to compute rotational distance between edges of start point and end point
    def getRotationalDists(self, layout):
        start, target = self.getStartAndTargetLocs(layout)
        headLoc = self.getHeadAxes()[0]
        startVec = start-headLoc
        targetVec = target-headLoc
        return self.angleBetweenVectors(startVec, targetVec)

    #return horizontal and vertical distances separately
    def getPlanarDists(self, layout):
        startX, startY = self.targets[self.TARGETINI].getTargetKeyLocationProp()
        targetLoc, targetWall = self.targets[self.TARGETINI].getTargetLocationProp(layout)
        targetGridX, targetGridY = targetLoc
        if(targetWall.lower() != "back"):
            diagDist = 0
            if(targetWall.lower() == "ceiling"):
                part1 = self.getSurfaceWidthRemUp(startX, startY, "front")
                part2 = self.getSurfaceWidthRemDown(targetGridX, targetGridY, "ceiling")
                vdist = part1 + part2

                part1 = self.getSurfaceWidthRemLeft(startX, startY, "front")
                part2 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY, "ceiling")
                hdist = abs(part1 - part2)

                diagDist = sqrt(pow(vdist, 2) + pow(hdist, 2))
            elif(targetWall.lower() == "left"):
                part1 = self.getSurfaceWidthRemLeft(startX, startY, "front")
                part2 = self.getSurfaceWidthRemRight(targetGridX, targetGridY, "left")
                vdist = part1 + part2

                part1 = self.getSurfaceWidthRemUp(startX, startY, "front")
                part2 = self.getSurfaceWidthRemUp(targetGridX, targetGridY, "left")
                hdist = abs(part1 - part2)

                diagDist = sqrt(pow(vdist, 2) + pow(hdist, 2))
            elif(targetWall.lower() == "right"):
                part1 = self.getSurfaceWidthRemRight(startX, startY, "front")
                part2 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY, "right")
                vdist = part1 + part2

                part1 = self.getSurfaceWidthRemUp(startX, startY, "front")
                part2 = self.getSurfaceWidthRemUp(targetGridX, targetGridY, "right")
                hdist = abs(part1 - part2)

                diagDist = sqrt(pow(vdist, 2) + pow(hdist, 2))
            else:
                print "Invalid target wall"
            return diagDist
        else:
            # Calculate vertical distance across ceiling
            part1 = self.getSurfaceWidthRemUp(startX, startY, "front")
            part2 = self.getSurfaceLength("ceiling")
            part3 = self.getSurfaceWidthRemUp(targetGridX, targetGridY, "back")
            vDistanceCeiling = part1 + part2 + part3

            # Calculate vertical distance across floor
            part1 = self.getSurfaceWidthRemDown(startX, startY, "front")
            part2 = self.getSurfaceLength("floor")
            part3 = self.getSurfaceWidthRemDown(targetGridX, targetGridY, "back")
            vDistanceFloor = part1 + part2 + part3

            # Calculate vertical distance across left wall
            part1 = self.getSurfaceWidthRemLeft(startX, startY, "front")
            part2 = self.getSurfaceLength("left")
            part3 = self.getSurfaceWidthRemRight(targetGridX, targetGridY, "back")
            vDistanceLeft = part1 + part2 + part3

            # Calculate vertical distance across right wall
            part1 = self.getSurfaceWidthRemRight(startX, startY, "front")
            part2 = self.getSurfaceLength("right")
            part3 = self.getSurfaceWidthRemLeft(targetGridX, targetGridY, "back")
            vDistanceRight = part1 + part2 + part3

            # Calculate horizontal distance across ceiling and floor
            part1 = self.getSurfaceWidthRemRight(startX, startY, "front")
            part2 = self.getSurfaceWidthRemLeft(startX, startY, "back")
            hDistanceCeiling = abs(part1-part2)
            hDistanceFloor = hDistanceCeiling

            # Calculate horizontal distance across left rand right walls
            part1 = self.getSurfaceWidthRemUp(startX, startY, "front")
            part2 = self.getSurfaceWidthRemUp(startX, startY, "back")
            hDistanceLeft = abs(part1 - part2)
            hDistanceRight = hDistanceLeft

            # Find the real diagonal distances across all the walls
            distanceCeiling = sqrt(pow(hDistanceCeiling, 2) + pow(vDistanceCeiling, 2))
            distanceFloor = sqrt(pow(hDistanceFloor, 2) + pow(vDistanceFloor, 2))
            distanceLeft = sqrt(pow(hDistanceLeft, 2) + pow(vDistanceLeft, 2))
            distanceRight = sqrt(pow(hDistanceRight, 2) + pow(vDistanceRight, 2))

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

            return shortest


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

    def getSurfaceWidthRemLeft(self, realPointX, realPointY, wall): #TODO Are coordinates FROM TR or BR?
        wall = self.wallToPlaneIndex[wall.lower()]
        realEdgeX, realEdgeY = 0, realPointY
        wallTL = self.planes[wall][2]
        wallTR = self.planes[wall][3]
        wallBL = self.planes[wall][5]
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
        wallTL = self.planes[wall][2]
        wallTR = self.planes[wall][3]
        wallBL = self.planes[wall][5]
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
        wallTL = self.planes[wall][2]
        wallTR = self.planes[wall][3]
        wallBL = self.planes[wall][5]
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
        wallTL = self.planes[wall][2]
        wallTR = self.planes[wall][3]
        wallBL = self.planes[wall][5]
        pointHVec = wallTR - wallTL * realPointX
        pointVVec = wallBL - wallTL * realPointY
        edgeHVec = wallTR - wallTL * realEdgeX
        edgeVVec = wallBL - wallTL * realEdgeY
        point = wallTL + pointHVec + pointVVec
        edge = wallTL + edgeHVec + edgeVVec
        return self.distBetweenPoints(point, edge)

    # Get the real world locations of the start and target points
    def getStartAndTargetLocs(self, layout):
        propStartX, propStartY = self.targets[self.TARGETINI].getTargetKeyLocationProp()
        targetLoc, targetWall = self.targets[self.TARGETINI].getTargetLocationProp(layout)
        propTargetX, propTargetY = targetLoc
        startWall = self.wallToPlaneIndex["front"]
        targetWall = self.wallToPlaneIndex[targetWall.lower()]
        # Get the 3D real world coordinates for the top left, bottom right and bottom left of each surface
        startWallTL = self.planes[startWall][2]
        startWallBR = self.planes[startWall][4]
        startWallBL = self.planes[startWall][5]
        targetWallTL = self.planes[targetWall][2]
        targetWallBR = self.planes[targetWall][4]
        targetWallBL = self.planes[targetWall][5]
        # Calculate the horizontal and vertical vectors that run along the top and left side of the walls and then convert them to the vectors to the start and target.
        startHVec = (startWallBR - startWallBL) * propStartX
        startVVec = (startWallTL - startWallBL) * propStartY
        targetHVec = (targetWallBR - targetWallBL) * propTargetX
        targetVVec = (targetWallTL - targetWallBL) * propTargetY
        # Use the calculated vectors to find the start and target 3D real world coordinates.
        start = startWallBL+startHVec+startVVec
        target = targetWallBL+targetHVec+targetVVec
        return start, target

    def clearTargetLayout(self):
        for x in range(0, len(self.visibleTargets)):
            projector, elementNo, canvasNo = self.visibleTargets[x]
            self.sender.removeElement(projector, elementNo, canvasNo)
            self.sender.removeElement(self.border[0], self.border[1], self.border[2])
        self.visibleTargets = []

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
            self.planes.append([content[0], content[1], content[2], content[3], content[4], content[5], content[6], content[7]])
            self.planes.append([content[8], content[9], content[10], content[11], content[12], content[13], content[14], content[15]])
            self.planes.append([content[16], content[17], content[18], content[19], content[20], content[21], content[22], content[23]])
            self.planes.append([content[24], content[25], content[26], content[27], content[28], content[29], content[30], content[31]])
            self.planes.append([content[32], content[33], content[34], content[35], content[36], content[37], content[38], content[39]])
            self.planes.append([content[40], content[41], content[42], content[43], content[44], content[45], content[46], content[47]])

            self.heights = {}
            self.widths = {}
            self.fullHeights = {}
            self.heights["front"] = (self.distBetweenPoints(content[2], content[5]) + self.distBetweenPoints(content[4], content[3]))/2
            self.widths["front"] = (self.distBetweenPoints(content[2], content[3]) + self.distBetweenPoints(content[5], content[4]))/2
            self.heights["right"] = (self.distBetweenPoints(content[10], content[13]) + self.distBetweenPoints(content[12], content[11]))/2
            self.widths["right"] = (self.distBetweenPoints(content[10], content[11]) + self.distBetweenPoints(content[13], content[12]))/2
            self.heights["back"] = (self.distBetweenPoints(content[18], content[21]) + self.distBetweenPoints(content[20], content[19]))/2
            self.widths["back"] = (self.distBetweenPoints(content[18], content[19]) + self.distBetweenPoints(content[21], content[20]))/2
            self.heights["left"] = (self.distBetweenPoints(content[26], content[29]) + self.distBetweenPoints(content[28], content[27]))/2
            self.widths["left"] = (self.distBetweenPoints(content[26], content[27]) + self.distBetweenPoints(content[29], content[28]))/2
            self.heights["ceiling"] = (self.distBetweenPoints(content[34], content[37]) + self.distBetweenPoints(content[36], content[35]))/2
            self.widths["ceiling"] = (self.distBetweenPoints(content[34], content[35]) + self.distBetweenPoints(content[37], content[36]))/2
            self.heights["floor"] = (self.distBetweenPoints(content[42], content[45]) + self.distBetweenPoints(content[44], content[43]))/2
            self.widths["floor"] = (self.distBetweenPoints(content[42], content[43]) + self.distBetweenPoints(content[45], content[44]))/2

            self.fullHeights["front"] = (self.distBetweenPoints(content[2], content[7]) + self.distBetweenPoints(content[6], content[3])) / 2
            self.fullHeights["right"] = (self.distBetweenPoints(content[10], content[15]) + self.distBetweenPoints(content[14], content[11])) / 2
            self.fullHeights["back"] = (self.distBetweenPoints(content[18], content[23]) + self.distBetweenPoints(content[22], content[19])) / 2
            self.fullHeights["left"] = (self.distBetweenPoints(content[26], content[31]) + self.distBetweenPoints(content[30], content[27])) / 2

            self.upperProjectionProp = {}
            self.upperProjectionProp["front"] = self.heights["front"] / self.fullHeights["front"]
            self.upperProjectionProp["right"] = self.heights["right"] / self.fullHeights["right"]
            self.upperProjectionProp["back"] = self.heights["back"] / self.fullHeights["back"]
            self.upperProjectionProp["left"] = self.heights["left"] / self.fullHeights["left"]
            self.upperProjectionProp["ceiling"] = 1.0

            self.roomDepth = (self.heights["ceiling"] + self.heights["floor"] + self.widths["left"] + self.widths["right"])/4
            self.roomWidth = (self.widths["front"] + self.widths["back"] + self.widths["ceiling"] + self.widths["floor"])/4
            self.roomHeight = (self.fullHeights["front"] + self.fullHeights["left"] + self.fullHeights["right"] + self.fullHeights["back"]) / 4

    # def loadOrderFile(self, filename):


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


        tkinterThread = threading.Thread(target=self.tkinthread, args=())  # Creates the display thread
        tkinterThread.start()  # Starts the display thread

        thread = Thread(target=self.serverInit, args=())
        thread.start()

        self.sender = messageSender()
        self.winWidth = 640
        self.winHeight = 480

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
        self.sender.loadDefinedSurfaces(2, "Test1Wall")
        self.sender.loadDefinedSurfaces(1, "AllMinusFront")
        self.loadWallCoordinates('layout.csv')
        self.initGUI()
        self.state = 0

        self.mouseLock = False
        pygame.mouse.set_visible(False)

        mouseThread = threading.Thread(target=self.mouseMovement, args=())  # Creates the display thread
        mouseThread.start()  # Starts the display thread
        self.currentLayout = 1
        now = datetime.datetime.now()

        self.targets = {}
        order = {}
        foundLayouts = []
        with open("order1.csv", "rb") as f:
            records = csv.DictReader(f)
            for row in records:
                order[row['number']] = row
                if row['targetfile'] not in foundLayouts:
                    foundLayouts.append(row['targetfile'])
        for x in range(0, len(foundLayouts)):
            self.TARGETINI = foundLayouts[x]  # Makes sure that the last layout is used to check the room details
            print "Scanning Layout " + foundLayouts[x]
            self.targets[foundLayouts[x]] = Targets()
            self.targets[foundLayouts[x]].parseFile(foundLayouts[x])
            self.targets[foundLayouts[x]].setHeightsAndWidths(self.heights, self.widths)
            print "Layout scanned\n\n"

        # Check if trialResults file exists already
        exists = os.path.isfile("results/" + str(self.USERNO) + "_trialResults.csv")
        orderIndex = 1
        newFile = False
        writingPermissions = 'w'
        if not exists:
            newFile = True
        else:
            i = 0
            with open("results/" + str(self.USERNO) + "_trialResults.csv") as f:
                for i, l in enumerate(f):
                    pass
            orderIndex = i+1
            writingPermissions = 'a'
            for filename in glob.glob("results/" + str(self.USERNO) + "_trace_*"):
                file = filename.split("/")[1]
                file = file.split("_")
                condition1 = file[2]
                condition2 = file[3]
                self.incrementTrialNumForCond(condition1, condition2)
            print "Results file already exists. Starting with " + str(orderIndex)

        if newFile:
            with open("results/" + str(self.USERNO) + "_trialDetails.csv", 'w') as trialDetailsCSV:
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
                              'target_dim_prop_F',
                              'target_dim_prop_B',
                              'target_dim_prop_R',
                              'target_dim_prop_L',
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
                                 'key_location_prop': str(self.targets[self.TARGETINI].getTargetKeyLocationProp()[0]) + "," +
                                                 str(self.targets[self.TARGETINI].getTargetKeyLocationProp()[1]),
                                 'target_dim_prop_F': str(self.targets[self.TARGETINI].getTargetDimensionProp('front')[0]) + "," +
                                                   str(self.targets[self.TARGETINI].getTargetDimensionProp('front')[1]),
                                 'target_dim_prop_B': str(self.targets[self.TARGETINI].getTargetDimensionProp('back')[0]) + "," +
                                                   str(self.targets[self.TARGETINI].getTargetDimensionProp('back')[1]),
                                 'target_dim_prop_R': str(self.targets[self.TARGETINI].getTargetDimensionProp('right')[0]) + "," +
                                                   str(self.targets[self.TARGETINI].getTargetDimensionProp('right')[1]),
                                 'target_dim_prop_L': str(self.targets[self.TARGETINI].getTargetDimensionProp('left')[0]) + "," +
                                                   str(self.targets[self.TARGETINI].getTargetDimensionProp('left')[1]),
                                 'target_dim_prop_C': str(self.targets[self.TARGETINI].getTargetDimensionProp('ceiling')[0]) + "," +
                                                   str(self.targets[self.TARGETINI].getTargetDimensionProp('ceiling')[1])})

        with open("results/" + str(self.USERNO) + "_trialResults.csv", writingPermissions) as trialDetailsCSV:
            fieldnames = ['condition1',  # pointing vs perspective
                          'condition2',  # Synchronous vs asychronous
                          'target_ini',
                          'target_layout',
                          'no_distractors_long',
                          'no_distractors_square',
                          'trial_num_cond',
                          'direct_dist',
                          'angular_dist',
                          'surface_dist',
                          'trace_file',
                          'trace_distance',
                          'trace_angular_distance',
                          'target_icon',
                          'target_location',
                          'front_icons_tall',
                          'front_icons_wide',
                          'back_icons_tall',
                          'back_icons_wide',
                          'left_icons_tall',
                          'left_icons_wide',
                          'right_icons_tall',
                          'right_icons_wide',
                          'ceiling_icons_tall',
                          'ceiling_icons_wide',
                          'icon_width',
                          'key_click_time',
                          'key_click_date',
                          'target_click_time',
                          'target_click_date',
                          'head_coordinates',  # For perspective
                          'tracker_coordinates',  # For pointing
                          'finding_duration',  # For asynchronous
                          'moving_duration',
                          'max_mouse_angular_velocity',
                          'max_mouse_velocity',
                          'no_walls_passed',
                          'no_walls_needed'
                          ]
            writer = csv.DictWriter(trialDetailsCSV, fieldnames=fieldnames)
            if newFile:
                writer.writeheader()
            #self.loadOrderFile()

            if (self.quit == False):
                while (self.quit == False):
                    self.background.fill((255, 255, 255))
                    text = self.font.render("", 1, (10, 10, 10))
                    textpos = text.get_rect()
                    textpos.centerx = self.background.get_rect().centerx
                    self.background.blit(text, textpos)
                    self.getInput(False)

                    self.currentLayout = int(order[str(orderIndex)]['layout'])
                    self.TARGETINI = order[str(orderIndex)]['targetfile']
                    CONDITION1 = order[str(orderIndex)]['condition1']
                    if CONDITION1 == "pointing":
                        self.mouseTask = False
                    else:
                        self.mouseTask = True
                    CONDITION2 = order[str(orderIndex)]['condition2']
                    if CONDITION2 == "synchronous":
                        self.parallelTask = True
                    else:
                        self.parallelTask = False

                    # Run experimental process
                    if self.state == 0:
                        self.drawKeyLayout(self.currentLayout)
                        if not self.parallelTask:
                            self.drawTargetLayout(self.currentLayout)
                            self.state = 0.5
                            self.foundClick = False
                            self.findTimer = datetime.datetime.now()
                        else:
                            self.state = 1
                            self.keyHit = False
                    elif self.state == 0.5:
                        if self.foundClick:
                            clicktime = datetime.datetime.now()
                            self.clickelapsedsecs = (clicktime - self.findTimer)
                            self.state = 1
                            self.keyHit = False
                    elif self.state == 1:
                        if self.keyHit:
                            if self.parallelTask:
                                self.drawTargetLayout(self.currentLayout)
                            self.sender.setRectangleLineColor(self.border[0], self.border[1], (0, 1, 0, 1))
                            self.keyClickTime = datetime.datetime.now()
                            self.currentPath = []
                            self.passedSurfaces = 0
                            self.currentSurface = 'front'
                            self.state = 2
                            self.targetHit = False

                    elif self.state == 2:
                        if self.targetHit:
                            self.state = 0
                            self.targetClickTime = datetime.datetime.now()
                            targetWall = self.targets[self.TARGETINI].getTargetLocation(self.currentLayout)[1]
                            wallsneeded = 0
                            if targetWall == "back":
                                wallsneeded = 3
                            elif targetWall == "front":
                                wallsneeded = 1
                            else:
                                wallsneeded = 2
                            recordedPath = self.currentPath
                            self.currentPath = []
                            elapsedSecs = (self.targetClickTime - self.keyClickTime).total_seconds()
                            headLoc = self.getHeadAxes()[0]
                            trackerLoc = self.getTrackerData()[0][0]
                            self.incrementTrialNumForCond(CONDITION1, CONDITION2)
                            if self.parallelTask:
                                self.clickelapsedsecs = 0
                            targetLocation = self.targets[self.TARGETINI].getTargetLocation(self.currentLayout)
                            writer.writerow({'condition1': CONDITION1,  # pointing vs perspective
                                             'condition2': CONDITION2,  # Synchronous vs asychronous
                                             'target_ini': self.TARGETINI,
                                             'target_layout': self.currentLayout,
                                             'no_distractors_long': self.targets[self.TARGETINI].getTargetCountLongSurface(),
                                             'no_distractors_square': self.targets[self.TARGETINI].getTargetCountSquareSurface(),
                                             'trial_num_cond': self.getTrialNumForCond(CONDITION1, CONDITION2),
                                             'direct_dist': self.getDirectDists(self.currentLayout),
                                             'angular_dist': self.getRotationalDists(self.currentLayout),
                                             'surface_dist': self.getPlanarDists(self.currentLayout),
                                             'trace_file': "trace_" + CONDITION1 + "_" + CONDITION2 + "_" +
                                                           str(self.getTrialNumForCond(CONDITION1, CONDITION2)) + ".csv",
                                             'trace_distance': str(self.pathLength(recordedPath)),
                                             'trace_angular_distance': str(self.pathAngle(recordedPath)),
                                             'target_icon': self.targets[self.TARGETINI].getTargetIcon(self.currentLayout),
                                             'target_location': self.targets[self.TARGETINI].getTargetLocationProp(self.currentLayout),
                                             'front_icons_tall': self.targets[self.TARGETINI].getFrontIconsTall(),
                                             'front_icons_wide': self.targets[self.TARGETINI].getFrontIconsWide(),
                                             'back_icons_tall': self.targets[self.TARGETINI].getBackIconsTall(),
                                             'back_icons_wide': self.targets[self.TARGETINI].getBackIconsWide(),
                                             'left_icons_tall': self.targets[self.TARGETINI].getLeftIconsTall(),
                                             'left_icons_wide': self.targets[self.TARGETINI].getLeftIconsWide(),
                                             'right_icons_tall': self.targets[self.TARGETINI].getRightIconsTall(),
                                             'right_icons_wide': self.targets[self.TARGETINI].getRightIconsWide(),
                                             'ceiling_icons_tall': self.targets[self.TARGETINI].getCeilingIconsTall(),
                                             'ceiling_icons_wide': self.targets[self.TARGETINI].getCeilingIconsWide(),
                                             'icon_width': self.targets[self.TARGETINI].getTargetDimension(),
                                             'key_click_time': str(self.keyClickTime.time().hour).zfill(2) + ":" +
                                                           str(self.keyClickTime.time().minute).zfill(2) + ":" +
                                                           str(self.keyClickTime.time().second).zfill(2),
                                             'key_click_date': str(self.keyClickTime.date().day).zfill(2) + "/" +
                                                           str(self.keyClickTime.date().month).zfill(2) + "/" +
                                                           str(self.keyClickTime.date().year),
                                             'target_click_time': str(self.targetClickTime.time().hour).zfill(2) + ":" +
                                                           str(self.targetClickTime.time().minute).zfill(2) + ":" +
                                                           str(self.targetClickTime.time().second).zfill(2),
                                             'target_click_date': str(self.targetClickTime.date().day).zfill(2) + "/" +
                                                           str(self.targetClickTime.date().month).zfill(2) + "/" +
                                                           str(self.targetClickTime.date().year),
                                             'head_coordinates': str(headLoc[0]) + "," +
                                                                 str(headLoc[1]),  # For perspective
                                             'tracker_coordinates': str(trackerLoc[0]) + "," +
                                                                    str(trackerLoc[1]),  # For pointing
                                             'finding_duration': str(self.clickelapsedsecs),  # For asynchronous
                                             'moving_duration': elapsedSecs,
                                             'max_mouse_angular_velocity': self.fastestAngularVelocity(recordedPath),
                                             'max_mouse_velocity': self.fastestVelocity(recordedPath),
                                             'no_walls_passed': self.passedSurfaces,
                                             'no_walls_needed': wallsneeded})
                            #self.incrementTrialNumCond(self.CONDITION1, self.CONDITION2)
                            self.clearTargetLayout()
                            pathWriteThread = threading.Thread(target=self.writePathFile, args=([CONDITION1, CONDITION2,
                                                                                                recordedPath]))
                            pathWriteThread.start()
                            writer = csv.DictWriter(trialDetailsCSV, fieldnames=fieldnames)
                            self.alreadyPassed = ['front']
                            orderIndex += 1
                    self.screen.blit(self.background, (0, 0))
                    pygame.display.flip()
                    time.sleep(1 / 30)
                    if orderIndex > len(order):
                        break
        time.sleep(0.2)
        pygame.quit()

    def writePathFile(self, CONDITION1, CONDITION2, recordedPath):
        with open("results/" + str(self.USERNO) + "_trace_" + CONDITION1 + "_" + CONDITION2 + "_" +
                          str(self.getTrialNumForCond(CONDITION1, CONDITION2)) +
                          ".csv", 'w') as traceFile:
            traceFile.write("userLoc,startPoint,endPoint,distance,angle,angularVelocity,velocity\n")
            for index in range(0, len(recordedPath)):
                traceFile.write(str(recordedPath[index]["userLoc"]) + "," +
                                str(recordedPath[index]["startPoint"]) + "," +
                                str(recordedPath[index]["endPoint"]) + "," +
                                str(recordedPath[index]["distance"]) + "," +
                                str(recordedPath[index]["angle"]) + "," +
                                str(recordedPath[index]["angularVelocity"]) + "," +
                                str(recordedPath[index]["velocity"]) + "," +
                                str(recordedPath[index]["time"]) + "\n")
        print "Wrote path file \"results/" + str(self.USERNO) + "_trace_" + CONDITION1 + "_" + CONDITION2 + "_" + str(self.getTrialNumForCond(CONDITION1, CONDITION2)) + ".csv\""

    def incrementTrialNumForCond(self, condition1, condition2):
        self.conditionCounter[condition1 + "," + condition2] += 1

    def getTrialNumForCond(self, condition1, condition2):
        return self.conditionCounter[condition1 + "," + condition2]

class Targets:
    CEILING_WIDE = None
    CEILING_TALL = None
    FRONT_WIDE = None
    FRONT_TALL = None
    BACK_WIDE = None
    BACK_TALL = None
    LEFT_WIDE = None
    LEFT_TALL = None
    RIGHT_WIDE = None
    RIGHT_TALL = None
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
        self.CEILING_WIDE = int(targetParser.get("configuration", "CEILING_WIDE"))
        self.CEILING_TALL = int(targetParser.get("configuration", "CEILING_TALL"))
        self.FRONT_WIDE = int(targetParser.get("configuration", "FRONT_WIDE"))
        self.FRONT_TALL = int(targetParser.get("configuration", "FRONT_TALL"))
        self.BACK_WIDE = int(targetParser.get("configuration", "BACK_WIDE"))
        self.BACK_TALL = int(targetParser.get("configuration", "BACK_TALL"))
        self.LEFT_WIDE = int(targetParser.get("configuration", "LEFT_WIDE"))
        self.LEFT_TALL = int(targetParser.get("configuration", "LEFT_TALL"))
        self.RIGHT_WIDE = int(targetParser.get("configuration", "RIGHT_WIDE"))
        self.RIGHT_TALL = int(targetParser.get("configuration", "RIGHT_TALL"))
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
        self.targetAreaFTall = 1.0/self.FRONT_TALL
        self.targetAreaFWide = 1.0/self.FRONT_WIDE
        self.targetAreaBTall = 1.0/self.BACK_TALL
        self.targetAreaBWide = 1.0/self.BACK_WIDE
        self.targetAreaLTall = 1.0/self.LEFT_TALL
        self.targetAreaLWide = 1.0/self.LEFT_WIDE
        self.targetAreaRTall = 1.0/self.RIGHT_TALL
        self.targetAreaRWide = 1.0/self.RIGHT_WIDE
        self.targetAreaCTall = 1.0/self.CEILING_TALL
        self.targetAreaCWide = 1.0/self.CEILING_WIDE

    def getCeilingIconsWide(self):
        return self.CEILING_WIDE

    def getCeilingIconsTall(self):
        return self.CEILING_TALL

    def getFrontIconsWide(self):
        return self.FRONT_WIDE

    def getFrontIconsTall(self):
        return self.FRONT_TALL

    def getBackIconsWide(self):
        return self.BACK_WIDE

    def getBackIconsTall(self):
        return self.BACK_TALL

    def getLeftIconsWide(self):
        return self.LEFT_WIDE

    def getLeftIconsTall(self):
        return self.LEFT_TALL

    def getRightIconsWide(self):
        return self.RIGHT_WIDE

    def getRightIconsTall(self):
        return self.RIGHT_TALL

    def getTargetCountLongSurface(self):
        return self.TARGET_COUNT_LONG_SURFACE

    def getTargetCountSquareSurface(self):
        return self.TARGET_COUNT_SQUARE_SURFACE

    def getTargetKeyLocation(self):
        return self.KEY_X, self.KEY_Y

    def getTargetKeyLocationProp(self):
        gridLoc = self.getTargetKeyLocation()
        locationX = (self.targetAreaFWide*gridLoc[0])-(self.targetAreaFWide/2)
        locationY = (self.targetAreaFTall*gridLoc[1])-(self.targetAreaFTall/2)
        return locationX, locationY

    def getTargetIcon(self, layout):
        return self.targets[layout]['target']

    def setHeightsAndWidths(self, heights, widths):
        self.heights = heights
        self.widths = widths
        walls = ["front", "left", "back", "right", "ceiling"]
        shortestDim = 0
        for x in range(0, len(walls)):
            ideal = self.getIdealTargetDimensions(walls[x])
            print str(ideal)
            if shortestDim == 0 or ideal[0] < shortestDim:
                print "From " + str(shortestDim) + " to " + str(ideal[0])
                shortestDim = ideal[0]
            if ideal[1] < shortestDim:
                print "From " + str(shortestDim) + " to " + str(ideal[1])
                shortestDim = ideal[1]
        self.targetRealDimension = shortestDim

    def getIdealTargetDimensions(self, wall):
        widthFull = 0
        heightFull = 0
        if wall == "left":
            widthFull = self.targetAreaLWide * self.widths[wall]
            heightFull = self.targetAreaLTall * self.heights[wall]
        elif wall == "right":
            widthFull = self.targetAreaRWide * self.widths[wall]
            heightFull = self.targetAreaRTall * self.heights[wall]
        elif wall == "front":
            widthFull = self.targetAreaFWide * self.widths[wall]
            heightFull = self.targetAreaFTall * self.heights[wall]
        elif wall == "back":
            widthFull = self.targetAreaBWide * self.widths[wall]
            heightFull = self.targetAreaBTall * self.heights[wall]
        elif wall == "ceiling":
            widthFull = self.targetAreaCWide * self.widths[wall]
            heightFull = self.targetAreaCTall * self.heights[wall]
        idealTargetWidth = 0.75*widthFull
        idealTargetHeight = 0.75*heightFull
        return idealTargetWidth, idealTargetHeight

    def getTargetDimension(self):
        return self.targetRealDimension, self.targetRealDimension

    def getTargetDimensionProp(self, wall):
        wallWidth = self.widths[wall]
        wallHeight = self.heights[wall]
        return self.targetRealDimension/wallWidth, self.targetRealDimension/wallHeight

    def getTargetLocation(self, layout):
        for x in range(0, self.TARGET_COUNT_SQUARE_SURFACE):
            target = self.targets[layout]["wallF"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "front"
        for x in range(0, self.TARGET_COUNT_SQUARE_SURFACE):
            target = self.targets[layout]["wallB"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "back"
        for x in range(0, self.TARGET_COUNT_LONG_SURFACE):
            target = self.targets[layout]["wallL"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "left"
        for x in range(0, self.TARGET_COUNT_LONG_SURFACE):
            target = self.targets[layout]["wallR"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "right"
        for x in range(0, self.TARGET_COUNT_LONG_SURFACE):
            target = self.targets[layout]["ceiling"][x]
            if target[1] == self.getTargetIcon(layout):
                return target[0], "ceiling"
        print "ERROR: Target not found among distractors. Poorly formed ini file."

    def getTargetLocationProp(self, layout):
        gridLoc = self.getTargetLocation(layout)
        locationX = 0
        locationY = 0
        wall = gridLoc[1]
        gridLoc = gridLoc[0]
        if wall.lower() == "front":
            locationX = (self.targetAreaFWide*gridLoc[0])-(self.targetAreaFWide/2)
            locationY = (self.targetAreaFTall*gridLoc[1])-(self.targetAreaFTall/2)
        elif wall.lower() == "back":
            locationX = (self.targetAreaBWide*gridLoc[0])-(self.targetAreaBWide/2)
            locationY = (self.targetAreaBTall*gridLoc[1])-(self.targetAreaBTall/2)
        elif wall.lower() == "left":
            locationX = (self.targetAreaLWide*gridLoc[0])-(self.targetAreaLWide/2)
            locationY = (self.targetAreaLTall*gridLoc[1])-(self.targetAreaLTall/2)
        elif wall.lower() == "right":
            locationX = (self.targetAreaRWide*gridLoc[0])-(self.targetAreaRWide/2)
            locationY = (self.targetAreaRTall*gridLoc[1])-(self.targetAreaRTall/2)
        elif wall.lower() == "ceiling":
            locationX = (self.targetAreaCWide*gridLoc[0])-(self.targetAreaCWide/2)
            locationY = (self.targetAreaCTall*gridLoc[1])-(self.targetAreaCTall/2)
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
        if wall.lower() == "front":
            locationX = (self.targetAreaFWide*gridLoc[0])-(self.targetAreaFWide/2)
            locationY = (self.targetAreaFTall*gridLoc[1])-(self.targetAreaFTall/2)
        elif wall.lower() == "back":
            locationX = (self.targetAreaBWide*gridLoc[0])-(self.targetAreaBWide/2)
            locationY = (self.targetAreaBTall*gridLoc[1])-(self.targetAreaBTall/2)
        elif wall.lower() == "left":
            locationX = (self.targetAreaLWide*gridLoc[0])-(self.targetAreaLWide/2)
            locationY = (self.targetAreaLTall*gridLoc[1])-(self.targetAreaLTall/2)
        elif wall.lower() == "right":
            locationX = (self.targetAreaRWide*gridLoc[0])-(self.targetAreaRWide/2)
            locationY = (self.targetAreaRTall*gridLoc[1])-(self.targetAreaRTall/2)
        elif wall.lower() == "ceiling":
            locationX = (self.targetAreaCWide*gridLoc[0])-(self.targetAreaCWide/2)
            locationY = (self.targetAreaCTall*gridLoc[1])-(self.targetAreaCTall/2)
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
