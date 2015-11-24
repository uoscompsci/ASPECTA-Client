from Tkinter import *
from messageSender import *
import pygame
import threading
import time
from pygame.locals import *
from math import sqrt
from bezier import *
from ConfigParser import SafeConfigParser
import datetime
import tkMessageBox


class Client:
    ppe = None
    cornerdrag = False
    quit = False
    topCircles = {}
    bottomCircles = {}
    leftCircles = {}
    rightCircles = {}
    topbz = {}
    bottombz = {}
    leftbz = {}
    rightbz = {}
    symbolicDrag = {}
    rightDragging = []
    dragging = []
    hideable = []
    orientation = {}
    mirrored = {}
    warpedSurf = {}
    bezierUpdates = {}  # [top,bottom,left,right]
    centerPoints = {}
    setuplines = True
    refreshrate = 0
    connections = []
    dontFlip = {}
    surfCur = {}
    mainCur = None
    controlCur = None
    surfCanvases = {}
    stretchRects = {}
    aspect_stretch_circles = {}
    stretching = []
    texRects = {}
    sideToCorners = {"top": ("tl", "tr"), "bottom": ("bl", "br"), "left": ("tl", "bl"), "right": ("tr", "br")}
    cursorMode = "default"
    dragSurf = "none"
    real_width_rect = {}
    real_width_counter = {}
    real_width_unit = {}
    real_height_rect = {}
    real_height_counter = {}
    real_height_unit = {}
    centSurfCirc = {}
    surfControlMode = "meas"
    surfaceControl = 0
    surface_count = 0

    cornerAdj = {"tl": (("tr", "top"), ("bl", "left")), "tr": (("tl", "top"), ("br", "right")),
                 "br": (("bl", "bottom"), ("tr", "right")), "bl": (("br", "bottom"), ("tl", "left"))}

    # Scan for beziers that need to be updated and call them to be updated when appropriate
    def bezier_update_tracker(self):
        while not self.quit:
            for x in range(0, len(self.bezierUpdates)):
                try:
                    if self.bezierUpdates[x][0]:
                        self.update_bezier("top", x)
                        self.update_mesh(x)
                        self.bezierUpdates[x][0] = False
                    if self.bezierUpdates[x][1]:
                        self.update_bezier("bottom", x)
                        self.update_mesh(x)
                        self.bezierUpdates[x][1] = False
                    if self.bezierUpdates[x][2]:
                        self.update_bezier("left", x)
                        self.update_mesh(x)
                        self.bezierUpdates[x][2] = False
                    if self.bezierUpdates[x][3]:
                        self.update_bezier("right", x)
                        self.update_mesh(x)
                        self.bezierUpdates[x][3] = False
                except:
                    pass
            time.sleep(1.0 / 60)

    @staticmethod
    def line_intersection(x1a, y1a, x2a, y2a, x1b, y1b, x2b, y2b):
        code = """
            float dx = x2a - x1a;
            float dy = y2a - y1a;
            float m1 = dy/dx;
            float c1 = y1a - m1 * x1a;

            dx = x2b - x1b;
            dy = y2b - y1b;
            float m2 = dy/dx;
            float c2 = y1b - m2 * x1b;

            py::list ret;
            if((m1-m2)!=0){
                float intersection_x = (c2-c1)/(m1-m2);
                float intersection_y = m1 * intersection_x + c1;
                ret.append(intersection_x);
                ret.append(intersection_y);
            }
            return_val = ret;

        """
        c_ret = inline(code, ['x1a', 'y1a', 'x2a', 'y2a', 'x1b', 'y1b', 'x2b', 'y2b'])
        if len(c_ret) == 0:
            print "No Intersection"
            return None
        else:
            return c_ret[0], c_ret[1]

    # Get the midpoint between two points
    @staticmethod
    def get_midpoints(point1, point2):
        return (float(point1[0]) + float(point2[0])) / float(2), (float(point1[1]) + float(point2[1])) / float(2)

    # Get the opposite curve control point by mirroring the point over the control point
    @staticmethod
    def opposite_control_point(point, control):
        return (float(point[0]) + (float(point[0]) - float(control[0])),
                float(point[1]) + (float(point[1]) - float(control[1])))

    # Halves the number of waypoints on the curve
    def reduce_side(self, circles, side, surface):
        if len(circles) > 3:
            count = (len(circles) - 1) / 2
            for x in list(reversed(range(0, count))):
                circle = circles[2 * x + 1]
                circles.pop(2 * x + 1)
                self.sender.removeElement(circle, 1)
            if side == "top":
                self.bezierUpdates[surface][0] = True
            elif side == "bottom":
                self.bezierUpdates[surface][1] = True
            elif side == "left":
                self.bezierUpdates[surface][2] = True
            elif side == "right":
                self.bezierUpdates[surface][3] = True

    # Doubles the number of waypoints on the curve
    def split_side(self, circles, side, surface):
        count = len(circles)
        if count < 17:  # Restrict to a maximum of 15 waypoints per side
            insert = []
            for x in range(1, count):
                point1 = self.sender.getCirclePosition(circles[x - 1])
                point2 = self.sender.getCirclePosition(circles[x])
                midpoint = self.get_midpoints((point1[0], point1[1]), (point2[0], point2[1]))
                insert.append(midpoint)
            for x in reversed(range(0, len(insert))):
                ele = self.sender.newCircle(1, insert[x][0], int(insert[x][1]), 7, "pix", (1, 0, 0, 0), 1, (0, 1, 0, 1),
                                            10)
                self.hideable.append(ele)
                circles.insert(x + 1, ele)
            if side == "top":
                self.bezierUpdates[surface][0] = True
            elif side == "bottom":
                self.bezierUpdates[surface][1] = True
            elif side == "left":
                self.bezierUpdates[surface][2] = True
            elif side == "right":
                self.bezierUpdates[surface][3] = True

    # Rebuilds the bezier curve for the requested surface side
    def update_bezier(self, side, surface):
        points = []
        circles = []
        if side == "top":
            circles = self.topCircles[surface]
        elif side == "bottom":
            circles = self.bottomCircles[surface]
        elif side == "left":
            circles = self.leftCircles[surface]
        elif side == "right":
            circles = self.rightCircles[surface]
        for x in range(0, len(circles)):
            pos = self.sender.getCirclePosition(circles[x])
            points.append((pos[0], pos[1]))
        calc = BezierCalc()
        if side == "top":
            curve = calc.getCurvePoints(points, self.ppe)
            self.sender.setLineStripContent(self.topbz[surface], curve)
            self.connection_update_check(surface, "tl")
            self.connection_update_check(surface, "tr")
        elif side == "bottom":
            curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
            self.sender.setLineStripContent(self.bottombz[surface], curve)
            self.connection_update_check(surface, "bl")
            self.connection_update_check(surface, "br")
        elif side == "left":
            curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
            self.sender.setLineStripContent(self.leftbz[surface], curve)
            self.connection_update_check(surface, "tl")
            self.connection_update_check(surface, "bl")
        elif side == "right":
            curve = calc.getCurvePoints(points, self.ppe)
            self.sender.setLineStripContent(self.rightbz[surface], curve)
            self.connection_update_check(surface, "tr")
            self.connection_update_check(surface, "br")

    # Tells you whether a click is within 10 pixels of a point
    @staticmethod
    def is_hit(point1, point2, radius):
        a = abs(float(point1[0]) - float(point2[0]))
        b = abs(float(point1[1]) - float(point2[1]))
        csq = pow(a, 2) + pow(b, 2)
        c = sqrt(csq)
        if c < float(radius):
            return True
        else:
            return False

    # Gathers the curve points for the requested surface and passes them to the server so that the mesh can be updated
    def update_mesh(self, surface):
        top_points = []
        for x in range(0, len(self.topCircles[surface])):
            top_points.append(self.sender.getCirclePosition(self.topCircles[surface][x]))
        bottom_points = []
        for x in range(0, len(self.bottomCircles[surface])):
            bottom_points.append(
                self.sender.getCirclePosition(self.bottomCircles[surface][len(self.bottomCircles[surface]) - 1 - x]))
        left_points = []
        for x in range(0, len(self.leftCircles[surface])):
            left_points.append(self.sender.getCirclePosition(self.leftCircles[surface][x]))
        right_points = []
        for x in range(0, len(self.rightCircles[surface])):
            right_points.append(
                self.sender.getCirclePosition(self.rightCircles[surface][len(self.rightCircles[surface]) - 1 - x]))
        self.sender.setSurfaceEdges(self.warpedSurf[surface], top_points, bottom_points, left_points, right_points)

    # Creates a visible line to indicate a connection between two corners of different surfaces or removes it if it exists. If appropriate sides are connected
    def create_connection_line(self, start, end, visualize_only):
        found = False
        for x in range(0, len(self.connections)):
            if not found:
                if (start[0] == self.connections[x][0][0] and start[1] == self.connections[x][0][1] and end[0] ==
                        self.connections[x][1][0] and end[1] == self.connections[x][1][1]):
                    found = True
                    self.sender.removeElement(self.connections[x][2], 1)
                    self.connections.pop(x)
                elif (end[0] == self.connections[x][0][0] and end[1] == self.connections[x][0][1] and start[0] ==
                        self.connections[x][1][0] and start[1] == self.connections[x][1][1]):
                    found = True
                    self.sender.removeElement(self.connections[x][2], 1)
                    self.connections.pop(x)
        if not found:
            start_location = None
            if start[1] == "tl":
                start_location = self.sender.getCirclePosition(self.topCircles[start[0]][0])
            elif start[1] == "tr":
                topend = len(self.topCircles[start[0]]) - 1
                start_location = self.sender.getCirclePosition(self.topCircles[start[0]][topend])
            elif start[1] == "br":
                start_location = self.sender.getCirclePosition(self.bottomCircles[start[0]][0])
            elif start[1] == "bl":
                botend = len(self.bottomCircles[start[0]]) - 1
                start_location = self.sender.getCirclePosition(self.bottomCircles[start[0]][botend])
            end_location = None
            if end[1] == "tl":
                end_location = self.sender.getCirclePosition(self.topCircles[end[0]][0])
            elif end[1] == "tr":
                topend = len(self.topCircles[end[0]]) - 1
                end_location = self.sender.getCirclePosition(self.topCircles[end[0]][topend])
            elif end[1] == "br":
                end_location = self.sender.getCirclePosition(self.bottomCircles[end[0]][0])
            elif end[1] == "bl":
                botend = len(self.bottomCircles[end[0]]) - 1
                end_location = self.sender.getCirclePosition(self.bottomCircles[end[0]][botend])
            ele = self.sender.newLine(1, start_location[0], start_location[1], end_location[0], end_location[1], "pix",
                                      (1, 0, 0, 1), 3)
            self.connections.append([(start[0], start[1]), (end[0], end[1]), ele])
        if not visualize_only:
            # look for created connections
            for x in range(len(self.connections)):
                if (self.connections[x][0][0] == start[0] and self.connections[x][0][1] == self.cornerAdj[start[1]][0][
                        0]):
                    if (self.connections[x][1][0] == end[0] and self.connections[x][1][1] == self.cornerAdj[end[1]][0][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                        self.cornerAdj[end[1]][0][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                           self.cornerAdj[end[1]][0][1])
                    if (self.connections[x][1][0] == end[0] and self.connections[x][1][1] == self.cornerAdj[end[1]][1][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                        self.cornerAdj[end[1]][1][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                           self.cornerAdj[end[1]][1][1])
                elif (self.connections[x][1][0] == start[0] and self.connections[x][1][1] ==
                        self.cornerAdj[start[1]][0][0]):
                    if (self.connections[x][0][0] == end[0] and self.connections[x][0][1] == self.cornerAdj[end[1]][0][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                        self.cornerAdj[end[1]][0][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                           self.cornerAdj[end[1]][0][1])
                    if (self.connections[x][0][0] == end[0] and self.connections[x][0][1] == self.cornerAdj[end[1]][1][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                        self.cornerAdj[end[1]][1][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0],
                                                           self.cornerAdj[end[1]][1][1])
                if (self.connections[x][0][0] == start[0] and self.connections[x][0][1] == self.cornerAdj[start[1]][1][
                        0]):
                    if (self.connections[x][1][0] == end[0] and self.connections[x][1][1] == self.cornerAdj[end[1]][0][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                        self.cornerAdj[end[1]][0][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                           self.cornerAdj[end[1]][0][1])
                    if (self.connections[x][1][0] == end[0] and self.connections[x][1][1] == self.cornerAdj[end[1]][1][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                        self.cornerAdj[end[1]][1][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                           self.cornerAdj[end[1]][1][1])
                elif (self.connections[x][1][0] == start[0] and self.connections[x][1][1] ==
                        self.cornerAdj[start[1]][1][0]):
                    if (self.connections[x][0][0] == end[0] and self.connections[x][0][1] == self.cornerAdj[end[1]][0][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                        self.cornerAdj[end[1]][0][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                           self.cornerAdj[end[1]][0][1])
                    if (self.connections[x][0][0] == end[0] and self.connections[x][0][1] == self.cornerAdj[end[1]][1][
                            0]):
                        if not found:
                            self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                        self.cornerAdj[end[1]][1][1])
                        else:
                            self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0],
                                                           self.cornerAdj[end[1]][1][1])

    # Checks whether a point movement should alter an existing visualised connection line
    def connection_update_check(self, surface, corner):
        for x in range(len(self.connections)):
            if (self.connections[x][0][0] == surface and self.connections[x][0][1] == corner or self.connections[x][1][
                    0] == surface and self.connections[x][1][1] == corner):
                start_location = None
                if self.connections[x][0][1] == "tl":
                    start_location = self.sender.getCirclePosition(self.topCircles[self.connections[x][0][0]][0])
                elif self.connections[x][0][1] == "tr":
                    topend = len(self.topCircles[self.connections[x][0][0]]) - 1
                    start_location = self.sender.getCirclePosition(self.topCircles[self.connections[x][0][0]][topend])
                elif self.connections[x][0][1] == "br":
                    start_location = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][0][0]][0])
                elif self.connections[x][0][1] == "bl":
                    botend = len(self.bottomCircles[self.connections[x][0][0]]) - 1
                    start_location = self.sender.getCirclePosition(
                        self.bottomCircles[self.connections[x][0][0]][botend])
                end_location = None
                if self.connections[x][1][1] == "tl":
                    end_location = self.sender.getCirclePosition(self.topCircles[self.connections[x][1][0]][0])
                elif self.connections[x][1][1] == "tr":
                    topend = len(self.topCircles[self.connections[x][1][0]]) - 1
                    end_location = self.sender.getCirclePosition(self.topCircles[self.connections[x][1][0]][topend])
                elif self.connections[x][1][1] == "br":
                    end_location = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][1][0]][0])
                elif self.connections[x][1][1] == "bl":
                    botend = len(self.bottomCircles[self.connections[x][1][0]]) - 1
                    end_location = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][1][0]][botend])
                self.sender.setLineStart(self.connections[x][2], start_location[0], start_location[1])
                self.sender.setLineEnd(self.connections[x][2], end_location[0], end_location[1])

    def increment_digit(self, element_number):
        value = int(self.sender.getText(element_number))
        if value < 9:
            self.sender.setText(element_number, str(value + 1))
        else:
            self.sender.setText(element_number, str(0))

    def decrement_digit(self, element_number):
        value = int(self.sender.getText(element_number))
        if value > 0:
            self.sender.setText(element_number, str(value - 1))
        else:
            self.sender.setText(element_number, str(9))

    # Checks for mouse button and keyboard
    def get_input(self, get_point):
        # pos=pygame.mouse.get_pos() # mouse shift
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True
                return None
            elif event.type == pygame.KEYDOWN:
                pass
            if self.mouseLock:
                # Runs if a mouse button has been depressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Runs if the mouse wheel is being rolled upwards
                    if event.button == 4:
                        if self.controlCur == self.mainCur:
                            self.sender.rotateCursorClockwise(self.mainCur,
                                                              10)  # Tells the server to rotate the cursor clockwise
                        else:
                            if self.surfControlMode == "meas":
                                pos = self.sender.getCursorPosition(self.controlCur)
                                if pos[1] >= 512 - 75:
                                    if pos[0] > (512 / 2 - 80):
                                        if pos[0] < (512 / 2 - 50):
                                            self.increment_digit(self.real_width_counter[self.surfaceControl][0])
                                        elif pos[0] < (512 / 2 - 25):
                                            self.increment_digit(self.real_width_counter[self.surfaceControl][1])
                                        elif pos[0] < (512 / 2):
                                            self.increment_digit(self.real_width_counter[self.surfaceControl][2])
                                        elif pos[0] < (512 / 2 + 25):
                                            self.increment_digit(self.real_width_counter[self.surfaceControl][3])
                                elif 512 / 2 + 30 > pos[1] > 512 / 2 - 30:
                                    if pos[0] > 512 - 180:
                                        if pos[0] < 512 - 150:
                                            self.increment_digit(self.real_height_counter[self.surfaceControl][0])
                                        elif pos[0] < 512 - 125:
                                            self.increment_digit(self.real_height_counter[self.surfaceControl][1])
                                        elif pos[0] < 512 - 100:
                                            self.increment_digit(self.real_height_counter[self.surfaceControl][2])
                                        elif pos[0] < 512 - 75:
                                            self.increment_digit(self.real_height_counter[self.surfaceControl][3])
                    # Runs if the mouse wheel is being rolled downwards
                    elif event.button == 5:
                        if self.controlCur == self.mainCur:
                            self.sender.rotateCursorAnticlockwise(self.mainCur,
                                                                  10)  # Tells the server to rotate the cursor anticlockwise
                        else:
                            if self.surfControlMode == "meas":
                                pos = self.sender.getCursorPosition(self.controlCur)
                                if 512 - 75 <= pos[1] <= 512:
                                    if pos[0] > (512 / 2 - 80):
                                        if pos[0] < (512 / 2 - 50):
                                            self.decrement_digit(self.real_width_counter[self.surfaceControl][0])
                                        elif pos[0] < (512 / 2 - 25):
                                            self.decrement_digit(self.real_width_counter[self.surfaceControl][1])
                                        elif pos[0] < (512 / 2):
                                            self.decrement_digit(self.real_width_counter[self.surfaceControl][2])
                                        elif pos[0] < (512 / 2 + 25):
                                            self.decrement_digit(self.real_width_counter[self.surfaceControl][3])
                                elif 512 / 2 + 30 >= pos[1] >= 512 / 2 - 30:
                                    if pos[0] > 512 - 180:
                                        if pos[0] < 512 - 150:
                                            self.decrement_digit(self.real_height_counter[self.surfaceControl][0])
                                        elif pos[0] < 512 - 125:
                                            self.decrement_digit(self.real_height_counter[self.surfaceControl][1])
                                        elif pos[0] < 512 - 100:
                                            self.decrement_digit(self.real_height_counter[self.surfaceControl][2])
                                        elif pos[0] < 512 - 75:
                                            self.decrement_digit(self.real_height_counter[self.surfaceControl][3])
                    # Runs if the middle mouse button is pressed
                    elif event.button == 2:
                        self.middle_click_time = datetime.datetime.now()  # Saves the current time so that when the button is released click duration can be checked
                    # Runs if the right mouse button is pressed
                    elif event.button == 3:
                        self.right_click_time = datetime.datetime.now()  # Saves the current time so that when the button is released click duration can be checked
                        # Runs if the default cursor mode is active
                        if self.cursorMode == "default":
                            loc = self.sender.getCursorPosition(self.controlCur)
                            if self.controlCur == self.mainCur:
                                self.rightDragging = []
                                # Checks whether a corner point has been clicked and if so starts defining a connection
                                for z in range(0, len(self.topCircles)):
                                    hit = False
                                    point = self.sender.getCirclePosition(self.topCircles[z][0])
                                    radius = self.sender.getCircleRadius(self.topCircles[z][0])
                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                        self.rightDragging.append((self.topCircles[z][0], "tl", z))
                                        hit = True
                                    end = len(self.topCircles[z]) - 1
                                    point = self.sender.getCirclePosition(self.topCircles[z][end])
                                    radius = self.sender.getCircleRadius(self.topCircles[z][end])
                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                        self.rightDragging.append((self.topCircles[z][end], "tr", z))
                                        hit = True
                                    point = self.sender.getCirclePosition(self.bottomCircles[z][0])
                                    radius = self.sender.getCircleRadius(self.bottomCircles[z][0])
                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                        self.rightDragging.append((self.bottomCircles[z][0], "br", z))
                                        hit = True
                                    end = len(self.bottomCircles[z]) - 1
                                    point = self.sender.getCirclePosition(self.bottomCircles[z][end])
                                    radius = self.sender.getCircleRadius(self.bottomCircles[z][end])
                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                        self.rightDragging.append((self.bottomCircles[z][end], "bl", z))
                                        hit = True
                                    if hit:
                                        cirpos = self.sender.getCirclePosition(self.rightDragging[0][0])
                                        self.symbolicDrag[0] = self.sender.newLine(1, cirpos[0], cirpos[1], loc[0],
                                                                                   loc[1], "pix", (1, 0, 0, 1), 3)
                                        self.symbolicDrag[1] = self.sender.newCircle(1, loc[0], loc[1], 10, "pix",
                                                                                     (1, 0, 0, 0), 1, (1, 0, 0, 1), 10)
                    elif event.button == 1:
                        self.lClickTime = datetime.datetime.now()  # Saves the current time so that when the button is released click duration can be checked
                        if self.controlCur == self.mainCur:
                            # If the user is trying to create a corner point it is defined then returned
                            if get_point:
                                loc = self.sender.getCursorPosition(self.controlCur)
                                ele = self.sender.newCircle(1, loc[0], loc[1], 10, "pix", (1, 0, 0, 0), 1, (1, 1, 0, 1),
                                                            10)
                                self.hideable.append(ele)
                                return loc, ele
                            # If the user isn't trying to create a corner point it is checked whether they have clicked on an existing point so it can be dragged
                            else:
                                # Runs if the default cursor mode is active
                                if self.cursorMode == "default":
                                    loc = self.sender.getCursorPosition(self.controlCur)
                                    self.dragging = []
                                    self.cornerdrag = False
                                    for z in range(0, len(self.topCircles)):
                                        for x in range(0, len(self.topCircles[z])):
                                            point = self.sender.getCirclePosition(self.topCircles[z][x])
                                            if x == 0 or x == (len(self.topCircles[z]) - 1):
                                                radius = 10
                                            else:
                                                radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.dragSurf = str(z)
                                                self.dragging.append(self.topCircles[z][x])
                                                if x == 0 or x == (len(self.topCircles[z]) - 1):
                                                    self.cornerdrag = True
                                        for x in range(0, len(self.bottomCircles[z])):
                                            point = self.sender.getCirclePosition(self.bottomCircles[z][x])
                                            if x == 0 or x == (len(self.bottomCircles[z]) - 1):
                                                radius = 10
                                            else:
                                                radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.dragSurf = str(z)
                                                self.dragging.append(self.bottomCircles[z][x])
                                                if x == 0 or x == (len(self.bottomCircles[z]) - 1):
                                                    self.cornerdrag = True
                                        for x in range(0, len(self.leftCircles[z])):
                                            point = self.sender.getCirclePosition(self.leftCircles[z][x])
                                            if x == 0 or x == (len(self.leftCircles[z]) - 1):
                                                radius = 10
                                            else:
                                                radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.dragSurf = str(z)
                                                self.dragging.append(self.leftCircles[z][x])
                                                if x == 0 or x == (len(self.leftCircles[z]) - 1):
                                                    self.cornerdrag = True
                                        for x in range(0, len(self.rightCircles[z])):
                                            point = self.sender.getCirclePosition(self.rightCircles[z][x])
                                            if x == 0 or x == (len(self.rightCircles[z]) - 1):
                                                radius = 10
                                            else:
                                                radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.dragSurf = str(z)
                                                self.dragging.append(self.rightCircles[z][x])
                                                if x == 0 or x == (len(self.rightCircles[z]) - 1):
                                                    self.cornerdrag = True
                        else:
                            if self.surfControlMode == "aspect":
                                loc = self.sender.getCursorPosition(self.controlCur)
                                self.stretching = []
                                p = 0
                                if self.controlCur == self.surfCur[0]:
                                    p = 0
                                elif self.controlCur == self.surfCur[1]:
                                    p = 1
                                elif self.controlCur == self.surfCur[2]:
                                    p = 2
                                elif self.controlCur == self.surfCur[3]:
                                    p = 3
                                for q in range(len(self.aspect_stretch_circles[p])):
                                    point = self.sender.getCirclePosition(self.aspect_stretch_circles[p][q])
                                    radius = self.sender.getCircleRadius(self.aspect_stretch_circles[p][q])
                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                        self.stretching.append((p, q))
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Runs if the left mouse button has been released
                    if event.button == 1:
                        left_click_release_time = datetime.datetime.now()
                        click_duration = (
                            left_click_release_time - self.lClickTime).total_seconds()  # Checks how long the button was depressed
                        # Runs if the button was pressed for less than 0.15 seconds
                        if click_duration < 0.25:
                            if self.controlCur == self.mainCur:
                                # Runs if the default cursor mode is active
                                if self.cursorMode == "default":
                                    loc = self.sender.getCursorPosition(self.controlCur)
                                    for w in range(0, len(self.topCircles)):
                                        # If a waypoint has been clicked, the side it was part of is split so that there are twice as many waypoints
                                        for x in range(1, len(self.topCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.topCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.split_side(self.topCircles[w], "top", w)
                                                self.update_mesh(w)
                                        for x in range(1, len(self.bottomCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.bottomCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.split_side(self.bottomCircles[w], "bottom", w)
                                                self.update_mesh(w)
                                        for x in range(1, len(self.leftCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.leftCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.split_side(self.leftCircles[w], "left", w)
                                                self.update_mesh(w)
                                        for x in range(1, len(self.rightCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.rightCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                self.split_side(self.rightCircles[w], "right", w)
                                                self.update_mesh(w)
                                        # If a corner point has been clicked, the surface is mirrored or rotated as appropriate
                                        if not get_point:
                                            if not self.dontFlip[w]:
                                                flipped = False
                                                point = self.sender.getCirclePosition(self.topCircles[w][0])
                                                radius = 10
                                                if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                    if self.orientation[w] != 0:
                                                        if not self.mirrored[w]:
                                                            self.sender.rotateSurfaceTo0(w + 1)
                                                        else:
                                                            self.sender.rotateSurfaceTo270(w + 1)
                                                        self.orientation[w] = 0
                                                    else:
                                                        if not self.mirrored[w]:
                                                            self.sender.rotateSurfaceTo270(w + 1)
                                                            self.sender.mirrorSurface(w + 1)
                                                            self.mirrored[w] = True
                                                        else:
                                                            self.sender.rotateSurfaceTo0(w + 1)
                                                            self.sender.mirrorSurface(w + 1)
                                                            self.mirrored[w] = False
                                                    flipped = True
                                                if not flipped:
                                                    point = self.sender.getCirclePosition(
                                                        self.topCircles[w][len(self.topCircles[w]) - 1])
                                                    radius = 10
                                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                        if self.orientation[w] != 1:
                                                            if not self.mirrored[w]:
                                                                self.sender.rotateSurfaceTo90(w + 1)
                                                            else:
                                                                self.sender.rotateSurfaceTo0(w + 1)
                                                            self.orientation[w] = 1
                                                        else:
                                                            if not self.mirrored[w]:
                                                                self.sender.rotateSurfaceTo0(w + 1)
                                                                self.sender.mirrorSurface(w + 1)
                                                                self.mirrored[w] = True
                                                            else:
                                                                self.sender.rotateSurfaceTo90(w + 1)
                                                                self.sender.mirrorSurface(w + 1)
                                                                self.mirrored[w] = False
                                                        flipped = True
                                                if not flipped:
                                                    point = self.sender.getCirclePosition(self.bottomCircles[w][0])
                                                    radius = 10
                                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                        if self.orientation[w] != 2:
                                                            if not self.mirrored[w]:
                                                                self.sender.rotateSurfaceTo180(w + 1)
                                                            else:
                                                                self.sender.rotateSurfaceTo90(w + 1)
                                                            self.orientation[w] = 2
                                                        else:
                                                            if not self.mirrored[w]:
                                                                self.sender.rotateSurfaceTo90(w + 1)
                                                                self.sender.mirrorSurface(w + 1)
                                                                self.mirrored[w] = True
                                                            else:
                                                                self.sender.rotateSurfaceTo180(w + 1)
                                                                self.sender.mirrorSurface(w + 1)
                                                                self.mirrored[w] = False
                                                        flipped = True
                                                if not flipped:
                                                    point = self.sender.getCirclePosition(
                                                        self.bottomCircles[w][len(self.bottomCircles[w]) - 1])
                                                    radius = 10
                                                    if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                        if self.orientation[w] != 3:
                                                            if not self.mirrored[w]:
                                                                self.sender.rotateSurfaceTo270(w + 1)
                                                            else:
                                                                self.sender.rotateSurfaceTo180(w + 1)
                                                            self.orientation[w] = 3
                                                        else:
                                                            if not self.mirrored[w]:
                                                                self.sender.rotateSurfaceTo180(w + 1)
                                                                self.sender.mirrorSurface(w + 1)
                                                                self.mirrored[w] = True
                                                            else:
                                                                self.sender.rotateSurfaceTo270(w + 1)
                                                                self.sender.mirrorSurface(w + 1)
                                                                self.mirrored[w] = False
                                            else:
                                                self.dontFlip[w] = False
                                            for x in range(0, len(self.centerPoints)):
                                                point = self.sender.getCirclePosition(self.centerPoints[x])
                                                radius = 10
                                                if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                    self.controlCur = self.surfCur[x]
                                                    self.sender.hideCursor(self.mainCur)
                                                    for y in range(0, 4):
                                                        try:
                                                            self.sender.hideElement(self.centerPoints[y])
                                                        except KeyError, e:
                                                            pass
                                                    self.sender.showElement(self.centSurfCirc[x])
                                                    self.sender.setRectangleFillColor(self.real_width_rect[x],
                                                                                      (1, 0, 0, 1))
                                                    self.sender.setRectangleFillColor(self.real_height_rect[x],
                                                                                      (1, 0, 0, 1))
                                                    self.sender.relocateCursor(self.surfCur[x], 512 / 2, 512 / 2, "pix",
                                                                               self.warpedSurf[x])
                                                    self.sender.showCursor(self.surfCur[x])
                                                    self.surfaceControl = x
                            else:
                                loc = self.sender.getCursorPosition(self.controlCur)
                                x = self.surfaceControl
                                point = self.sender.getCirclePosition(self.centSurfCirc[x])
                                radius = 25
                                if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                    for y in range(0, 4):
                                        try:
                                            self.sender.showElement(self.aspect_stretch_circles[x][y])
                                        except KeyError, e:
                                            pass
                                    self.sender.showElement(self.stretchRects[x])
                                    self.sender.hideElement(self.centSurfCirc[x])
                                    self.sender.hideElement(self.real_width_rect[x])
                                    self.sender.hideElement(self.real_height_rect[x])
                                    for z in range(0, 4):
                                        self.sender.hideElement(self.real_width_counter[x][z])
                                        self.sender.hideElement(self.real_height_counter[x][z])
                                    self.sender.hideElement(self.real_width_unit[x])
                                    self.sender.hideElement(self.real_height_unit[x])

                                    self.surfControlMode = "aspect"
                        if self.controlCur == self.mainCur:
                            # If appropriate the list of points currently being dragged is cleared
                            for w in range(0, len(self.topCircles)):
                                if (len(self.topCircles[w]) > 1 and len(self.bottomCircles[w]) > 1 and len(
                                        self.leftCircles[w]) > 1 and len(self.rightCircles[w]) > 1):
                                    if len(self.dragging) != 0:
                                        self.dragging = []
                                        self.update_mesh(int(self.dragSurf))
                        else:
                            if len(self.stretching) > 0:
                                surface_width = self.sender.getSurfacePixelWidth(self.warpedSurf[self.stretching[0][0]])
                                surface_height = self.sender.getSurfacePixelHeight(
                                    self.warpedSurf[self.stretching[0][0]])
                                rectangle_width = self.sender.getRectangleWidth(
                                    self.stretchRects[self.stretching[0][0]])
                                rectangle_height = self.sender.getRectangleHeight(
                                    self.stretchRects[self.stretching[0][0]])

                                percent_width_rectangle = rectangle_width / surface_width * 100
                                percent_height_rectangle = rectangle_height / surface_height * 100
                                new_width = 150 / percent_width_rectangle * 100
                                new_height = 150 / percent_height_rectangle * 100

                                self.sender.setRectangleWidth(self.stretchRects[self.stretching[0][0]], 150, "pix")
                                self.sender.setRectangleHeight(self.stretchRects[self.stretching[0][0]], 150, "pix")
                                self.sender.setSurfacePixelWidth(self.warpedSurf[self.stretching[0][0]], int(new_width))
                                self.sender.setSurfacePixelHeight(self.warpedSurf[self.stretching[0][0]],
                                                                  int(new_height))
                                self.sender.relocateRectangle(self.stretchRects[self.stretching[0][0]],
                                                              new_width / 2 - 75, new_height / 2 + 75, "pix",
                                                              self.surfCanvases[
                                                                  self.warpedSurf[self.stretching[0][0]] - 1])
                                self.sender.relocateCircle(self.aspect_stretch_circles[self.stretching[0][0]][0],
                                                           new_width / 2,
                                                           new_height / 2 + 75, "pix",
                                                           self.surfCanvases[self.stretching[0][0]])
                                self.sender.relocateCircle(self.aspect_stretch_circles[self.stretching[0][0]][1],
                                                           new_width / 2,
                                                           new_height / 2 - 75, "pix",
                                                           self.surfCanvases[self.stretching[0][0]])
                                self.sender.relocateCircle(self.aspect_stretch_circles[self.stretching[0][0]][2],
                                                           new_width / 2 - 75, new_height / 2, "pix",
                                                           self.surfCanvases[self.stretching[0][0]])
                                self.sender.relocateCircle(self.aspect_stretch_circles[self.stretching[0][0]][3],
                                                           new_width / 2 + 75, new_height / 2, "pix",
                                                           self.surfCanvases[self.stretching[0][0]])
                                self.sender.setCircleRadius(self.aspect_stretch_circles[self.stretching[0][0]][0],
                                                            new_height * 20 / 512, "pix")
                                self.sender.setCircleRadius(self.aspect_stretch_circles[self.stretching[0][0]][1],
                                                            new_height * 20 / 512, "pix")
                                self.sender.setCircleRadius(self.aspect_stretch_circles[self.stretching[0][0]][2],
                                                            new_height * 20 / 512, "pix")
                                self.sender.setCircleRadius(self.aspect_stretch_circles[self.stretching[0][0]][3],
                                                            new_height * 20 / 512, "pix")
                            self.stretching = []
                    # Runs if the middle mouse button has been released
                    if event.button == 2:
                        middle_click_release_time = datetime.datetime.now()
                        click_duration = (
                            middle_click_release_time - self.middle_click_time).total_seconds()  # Checks how long the button was depressed
                        if self.controlCur == self.mainCur:
                            # Runs if the button was pressed for less than 0.25 seconds and unlocks the mouse from the server
                            if click_duration < 0.35:
                                self.mouseLock = False
                                pygame.mouse.set_visible(True)
                                self.master.focus_force()
                                self.sender.hideCursor(self.mainCur)
                        else:
                            if click_duration < 0.25:
                                if self.surfControlMode == "meas":
                                    current = None
                                    for x in range(0, len(self.surfCur)):
                                        if self.controlCur == self.surfCur[x]:
                                            current = x
                                    self.controlCur = self.mainCur
                                    self.sender.showCursor(self.mainCur)
                                    for x in range(0, 4):
                                        try:
                                            self.sender.showElement(self.centerPoints[x])
                                        except KeyError, e:
                                            pass
                                    self.sender.hideElement(self.centSurfCirc[current])
                                    self.sender.setRectangleFillColor(self.real_width_rect[current], (1, 1, 1, 1))
                                    self.sender.setRectangleFillColor(self.real_height_rect[current], (1, 1, 1, 1))
                                    self.sender.hideCursor(self.surfCur[current])
                                    stringvaluetop = self.sender.getText(self.real_width_counter[current][0])
                                    stringvaluetop += self.sender.getText(self.real_width_counter[current][1])
                                    stringvaluetop += self.sender.getText(self.real_width_counter[current][2])
                                    stringvaluetop += self.sender.getText(self.real_width_counter[current][3])
                                    valuetop = int(stringvaluetop)
                                    stringvalueright = self.sender.getText(self.real_height_counter[current][0])
                                    stringvalueright += self.sender.getText(self.real_height_counter[current][1])
                                    stringvalueright += self.sender.getText(self.real_height_counter[current][2])
                                    stringvalueright += self.sender.getText(self.real_height_counter[current][3])
                                    valueright = int(stringvalueright)
                                    self.sender.setSurfaceRealWidth(self.warpedSurf[current], valuetop)
                                    self.sender.setSurfaceRealHeight(self.warpedSurf[current], valueright)
                                    # self.sender.hideElement(self.stretchRects[current])
                                elif self.surfControlMode == "aspect":
                                    current = None
                                    for x in range(0, len(self.surfCur)):
                                        if self.controlCur == self.surfCur[x]:
                                            current = x
                                    self.surfControlMode = "meas"
                                    for x in range(0, 4):
                                        try:
                                            self.sender.hideElement(self.aspect_stretch_circles[current][x])
                                        except KeyError, e:
                                            pass
                                    self.sender.hideElement(self.stretchRects[current])
                                    self.sender.showElement(self.centSurfCirc[current])
                                    self.sender.showElement(self.real_width_rect[current])
                                    self.sender.showElement(self.real_height_rect[current])
                                    for z in range(0, 4):
                                        self.sender.showElement(self.real_width_counter[current][z])
                                        self.sender.showElement(self.real_height_counter[current][z])
                                    self.sender.showElement(self.real_width_unit[current])
                                    self.sender.showElement(self.real_height_unit[current])
                    # Runs if the right mouse button has been released
                    if event.button == 3:
                        right_click_release_time = datetime.datetime.now()
                        click_duration = (
                            right_click_release_time - self.right_click_time).total_seconds()  # Checks how long the button was depressed
                        if self.controlCur == self.mainCur:
                            hit = False
                            any_hits = False
                            # Runs if the button was pressed for less than 0.15 seconds
                            if click_duration < 0.25:
                                # Runs if the default cursor mode is active
                                if self.cursorMode == "default":
                                    loc = self.sender.getCursorPosition(self.controlCur)
                                    # If a waypoint has been clicked, the number of waypoints on the side is halved
                                    for w in range(0, len(self.topCircles)):
                                        for x in range(1, len(self.topCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.topCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                hit = True
                                                any_hits = True
                                        if hit:
                                            hit = False
                                            self.reduce_side(self.topCircles[w], "top", w)
                                            self.update_mesh(w)
                                        for x in range(1, len(self.bottomCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.bottomCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                hit = True
                                                any_hits = True
                                        if hit:
                                            hit = False
                                            self.reduce_side(self.bottomCircles[w], "bottom", w)
                                            self.update_mesh(w)
                                        for x in range(1, len(self.leftCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.leftCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                hit = True
                                                any_hits = True
                                        if hit:
                                            hit = False
                                            self.reduce_side(self.leftCircles[w], "left", w)
                                            self.update_mesh(w)
                                        for x in range(1, len(self.rightCircles[w]) - 1):
                                            point = self.sender.getCirclePosition(self.rightCircles[w][x])
                                            radius = 7
                                            if self.is_hit((point[0], point[1]), (loc[0], loc[1]), radius):
                                                hit = True
                                                any_hits = True
                                        if hit:
                                            hit = False
                                            self.reduce_side(self.rightCircles[w], "right", w)
                                            self.update_mesh(w)
                            drop_location = None
                            # The temporary connection line is deleted after its current end point is recorded
                            if len(self.symbolicDrag) > 0:
                                drop_location = self.sender.getCirclePosition(self.symbolicDrag[1])
                                self.sender.removeElement(self.symbolicDrag[0], 1)
                                self.sender.removeElement(self.symbolicDrag[1], 1)
                            # The list of items that were being dragged is scanned
                            for rDragInd in range(0, len(self.rightDragging)):
                                temp = self.rightDragging[rDragInd]
                                corner = temp[1]
                                surface = temp[2]
                                # If the dragged point was released over another point a connection line is created
                                for w in range(0, len(self.topCircles)):
                                    if w != surface:
                                        point = self.sender.getCirclePosition(self.topCircles[w][0])
                                        radius = 10
                                        if self.is_hit((point[0], point[1]), (drop_location[0], drop_location[1]),
                                                       radius):
                                            self.create_connection_line((surface, corner), (w, "tl"), False)
                                        end = len(self.topCircles[w]) - 1
                                        point = self.sender.getCirclePosition(self.topCircles[w][end])
                                        radius = 10
                                        if self.is_hit((point[0], point[1]), (drop_location[0], drop_location[1]),
                                                       radius):
                                            self.create_connection_line((surface, corner), (w, "tr"), False)
                                        point = self.sender.getCirclePosition(self.bottomCircles[w][0])
                                        radius = 10
                                        if self.is_hit((point[0], point[1]), (drop_location[0], drop_location[1]),
                                                       radius):
                                            self.create_connection_line((surface, corner), (w, "br"), False)
                                        end = len(self.bottomCircles[w]) - 1
                                        point = self.sender.getCirclePosition(self.bottomCircles[w][end])
                                        radius = 10
                                        if self.is_hit((point[0], point[1]), (drop_location[0], drop_location[1]),
                                                       radius):
                                            self.create_connection_line((surface, corner), (w, "bl"), False)
                            self.rightDragging = []
                            self.symbolicDrag = {}
                            # Runs if the button was pressed for less than 0.25 seconds and a point wasn't hit
                            if click_duration < 0.25 and not any_hits:
                                # Runs if the default cursor mode is active
                                if self.cursorMode == "default":
                                    # Switches to wall defining mode and begins definition if there are less than 4 walls, otherwise switches to screen defining mode
                                    if self.surface_count < 4:
                                        self.sender.setCursorWallMode(self.mainCur)
                                        self.cursorMode = "wall"
                                        self.define_surface()
                                        if self.sender.getCursorMode(self.mainCur) == "wall":
                                            self.split_side(self.topCircles[self.surface_count - 1], "top",
                                                            self.surface_count - 1)
                                            self.split_side(self.bottomCircles[self.surface_count - 1], "bottom",
                                                            self.surface_count - 1)
                                            self.split_side(self.leftCircles[self.surface_count - 1], "left",
                                                            self.surface_count - 1)
                                            self.split_side(self.rightCircles[self.surface_count - 1], "right",
                                                            self.surface_count - 1)
                                            self.sender.setCursorDefaultMode(1)
                                            self.cursorMode = "default"
                                    else:
                                        self.sender.setCursorScreenMode(self.mainCur)
                                        self.cursorMode = "screen"
                                # Runs if the wall defining cursor mode is active and switches to the screen defining mode
                                elif self.cursorMode == "wall":
                                    self.sender.setCursorScreenMode(self.mainCur)
                                    self.cursorMode = "screen"
                                # Runs if the screen defining cursor mode is active and switches to the blocked area defining mode
                                elif self.cursorMode == "screen":
                                    self.sender.setCursorBlockMode(self.mainCur)
                                    self.cursorMode = "block"
                                # Runs if the blocked area defining cursor mode is active and switches to the default defining mode
                                elif self.cursorMode == "block":
                                    self.sender.setCursorDefaultMode(self.mainCur)
                                    self.cursorMode = "default"
        return None

    # Loops until the program is closed and monitors mouse movement
    def mouse_movement(self):
        while not self.quit:
            time.sleep(1.0 / 60)
            if self.mouseLock:
                pos = pygame.mouse.get_pos()
                xdist = (self.winWidth / 2) - pos[0]
                ydist = (self.winHeight / 2) - pos[1]
                if not (xdist == 0 and ydist == 0):
                    pygame.mouse.set_pos([self.winWidth / 2, self.winHeight / 2])

                    self.sender.shiftCursor(self.controlCur, -xdist, ydist)

                    loc = self.sender.getCursorPosition(self.controlCur)
                    if len(self.dragging) != 0:
                        for x in range(0, len(self.dragging)):
                            self.sender.relocateCircle(self.dragging[x], float(loc[0]), float(loc[1]), "pix", 1)
                            for y in range(0, len(self.bezierUpdates)):
                                try:
                                    if self.topCircles[y].__contains__(self.dragging[x]):
                                        self.bezierUpdates[y][0] = True
                                        if self.cornerdrag:
                                            tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
                                            trcoor = self.sender.getCirclePosition(
                                                self.topCircles[y][len(self.topCircles[y]) - 1])
                                            brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
                                            blcoor = self.sender.getCirclePosition(
                                                self.bottomCircles[y][len(self.bottomCircles[y]) - 1])
                                            center = self.line_intersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1],
                                                                            trcoor[0], trcoor[1], blcoor[0], blcoor[1])
                                            self.sender.relocateCircle(self.centerPoints[y], center[0], center[1],
                                                                       "pix", 1)
                                    if self.bottomCircles[y].__contains__(self.dragging[x]):
                                        self.bezierUpdates[y][1] = True
                                        if self.cornerdrag:
                                            tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
                                            trcoor = self.sender.getCirclePosition(
                                                self.topCircles[y][len(self.topCircles[y]) - 1])
                                            brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
                                            blcoor = self.sender.getCirclePosition(
                                                self.bottomCircles[y][len(self.bottomCircles[y]) - 1])
                                            center = self.line_intersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1],
                                                                            trcoor[0], trcoor[1], blcoor[0], blcoor[1])
                                            self.sender.relocateCircle(self.centerPoints[y], center[0], center[1],
                                                                       "pix", 1)
                                    if self.leftCircles[y].__contains__(self.dragging[x]):
                                        self.bezierUpdates[y][2] = True
                                        if self.cornerdrag:
                                            tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
                                            trcoor = self.sender.getCirclePosition(
                                                self.topCircles[y][len(self.topCircles[y]) - 1])
                                            brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
                                            blcoor = self.sender.getCirclePosition(
                                                self.bottomCircles[y][len(self.bottomCircles[y]) - 1])
                                            center = self.line_intersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1],
                                                                            trcoor[0], trcoor[1], blcoor[0], blcoor[1])
                                            self.sender.relocateCircle(self.centerPoints[y], center[0], center[1],
                                                                       "pix", 1)
                                    if self.rightCircles[y].__contains__(self.dragging[x]):
                                        self.bezierUpdates[y][3] = True
                                        if self.cornerdrag:
                                            tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
                                            trcoor = self.sender.getCirclePosition(
                                                self.topCircles[y][len(self.topCircles[y]) - 1])
                                            brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
                                            blcoor = self.sender.getCirclePosition(
                                                self.bottomCircles[y][len(self.bottomCircles[y]) - 1])
                                            center = self.line_intersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1],
                                                                            trcoor[0], trcoor[1], blcoor[0], blcoor[1])
                                            self.sender.relocateCircle(self.centerPoints[y], center[0], center[1],
                                                                       "pix", 1)
                                except:
                                    pass
                    if len(self.rightDragging) != 0:
                        try:
                            self.sender.relocateCircle(self.symbolicDrag[1], float(loc[0]), float(loc[1]), "pix", 1)
                            self.sender.setLineEnd(self.symbolicDrag[0], float(loc[0]), float(loc[1]))
                        except:
                            pass
                    if len(self.stretching) != 0:
                        for x in self.stretching:
                            origpos = self.sender.getCirclePosition(self.aspect_stretch_circles[x[0]][x[1]])
                            wid = self.sender.getSurfacePixelWidth(self.warpedSurf[x[0]])
                            hei = self.sender.getSurfacePixelHeight(self.warpedSurf[x[0]])
                            if x[1] < 2:
                                if x[1] == 0 and loc[1] > hei / 2 or x[1] == 1 and loc[1] < hei / 2:
                                    self.sender.relocateCircle(self.aspect_stretch_circles[x[0]][x[1]],
                                                               float(origpos[0]),
                                                               float(loc[1]), "pix", self.surfCanvases[x[0]])
                                    hdifference = loc[1] - origpos[1]
                                    if x[1] == 0:
                                        origpos2 = self.sender.getCirclePosition(self.aspect_stretch_circles[x[0]][1])
                                        self.sender.relocateCircle(self.aspect_stretch_circles[x[0]][1],
                                                                   float(origpos[0]),
                                                                   float(origpos2[1]) - hdifference, "pix",
                                                                   self.surfCanvases[x[0]])
                                    else:
                                        origpos2 = self.sender.getCirclePosition(self.aspect_stretch_circles[x[0]][0])
                                        self.sender.relocateCircle(self.aspect_stretch_circles[x[0]][0],
                                                                   float(origpos[0]),
                                                                   float(origpos2[1]) - hdifference, "pix",
                                                                   self.surfCanvases[x[0]])
                            else:
                                if x[1] == 2 and loc[0] < wid / 2 or x[1] == 3 and loc[0] > wid / 2:
                                    self.sender.relocateCircle(self.aspect_stretch_circles[x[0]][x[1]], float(loc[0]),
                                                               float(origpos[1]), "pix", self.surfCanvases[x[0]])
                                    vdifference = loc[0] - origpos[0]
                                    if x[1] == 2:
                                        origpos2 = self.sender.getCirclePosition(self.aspect_stretch_circles[x[0]][3])
                                        self.sender.relocateCircle(self.aspect_stretch_circles[x[0]][3],
                                                                   float(origpos2[0]) - vdifference, float(origpos[1]),
                                                                   "pix", self.surfCanvases[x[0]])
                                    else:
                                        origpos2 = self.sender.getCirclePosition(self.aspect_stretch_circles[x[0]][2])
                                        self.sender.relocateCircle(self.aspect_stretch_circles[x[0]][2],
                                                                   float(origpos2[0]) - vdifference, float(origpos[1]),
                                                                   "pix", self.surfCanvases[x[0]])
                            self.update_rectangle(x[0])

    def update_rectangle(self, surface_rectangle_number):
        top = self.sender.getCirclePosition(self.aspect_stretch_circles[surface_rectangle_number][0])[1]
        bottom = self.sender.getCirclePosition(self.aspect_stretch_circles[surface_rectangle_number][1])[1]
        left = self.sender.getCirclePosition(self.aspect_stretch_circles[surface_rectangle_number][2])[0]
        right = self.sender.getCirclePosition(self.aspect_stretch_circles[surface_rectangle_number][3])[0]
        height = abs(top - bottom)
        width = abs(left - right)
        self.sender.setRectangleHeight(self.stretchRects[surface_rectangle_number], height, "pix")
        self.sender.setRectangleWidth(self.stretchRects[surface_rectangle_number], width, "pix")
        self.sender.relocateRectangle(self.stretchRects[surface_rectangle_number], left, top, "pix",
                                      self.surfCanvases[surface_rectangle_number])

    # Defines all required surfaces according to a layout data structure
    def redefine_surface(self, layout):
        for x in range(0, len(layout)):
            self.orientation[self.surface_count] = 0
            self.mirrored[self.surface_count] = False

            self.topCircles[self.surface_count] = []
            self.bottomCircles[self.surface_count] = []
            self.leftCircles[self.surface_count] = []
            self.rightCircles[self.surface_count] = []
            self.bezierUpdates[self.surface_count] = [False, False, False, False]

            y = 0
            for z in range(0, len(layout[x][y])):
                if z == 0:
                    self.topbz[self.surface_count] = self.sender.newLineStrip(1, layout[x][y][z][0],
                                                                              layout[x][y][z][1], "pix",
                                                                              (0, 0.75, 0, 1), 5)
                else:
                    self.sender.addLineStripPoint(self.topbz[self.surface_count], layout[x][y][z][0],
                                                  layout[x][y][z][1], "pix")
                ele = None
                if (z == 0) or (z == (len(layout[x][y]) - 1)):
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, "pix", (1, 0, 0, 0), 1,
                                                (1, 1, 0, 1), 10)
                else:
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, "pix", (1, 0, 0, 0), 1,
                                                (0, 1, 0, 1), 10)
                self.topCircles[self.surface_count].append(ele)
            y = 1
            for z in list(reversed(range(0, len(layout[x][y])))):
                if z == len(layout[x][y]) - 1:
                    self.bottombz[self.surface_count] = self.sender.newLineStrip(1, layout[x][y][z][0],
                                                                                 layout[x][y][z][1], "pix",
                                                                                 (0, 0.75, 0, 1), 5)
                else:
                    self.sender.addLineStripPoint(self.bottombz[self.surface_count], layout[x][y][z][0],
                                                  layout[x][y][z][1], "pix")
                ele = None
                if (z == 0) or (z == (len(layout[x][y]) - 1)):
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, "pix", (1, 0, 0, 0), 1,
                                                (1, 1, 0, 1), 10)
                else:
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, "pix", (1, 0, 0, 0), 1,
                                                (0, 1, 0, 1), 10)
                self.bottomCircles[self.surface_count].append(ele)
            y = 2
            for z in range(0, len(layout[x][y])):
                if z == 0:
                    self.leftbz[self.surface_count] = self.sender.newLineStrip(1, layout[x][y][z][0],
                                                                               layout[x][y][z][1], "pix",
                                                                               (0, 0.75, 0, 1), 5)
                else:
                    self.sender.addLineStripPoint(self.leftbz[self.surface_count], layout[x][y][z][0],
                                                  layout[x][y][z][1], "pix")
                ele = None
                if (z == 0) or (z == (len(layout[x][y]) - 1)):
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, "pix", (1, 0, 0, 0), 1,
                                                (1, 1, 0, 1), 10)
                else:
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, "pix", (1, 0, 0, 0), 1,
                                                (0, 1, 0, 1), 10)
                self.leftCircles[self.surface_count].append(ele)
            y = 3
            for z in list(reversed(range(0, len(layout[x][y])))):
                if z == len(layout[x][y]) - 1:
                    self.rightbz[self.surface_count] = self.sender.newLineStrip(1, layout[x][y][z][0],
                                                                                layout[x][y][z][1], "pix",
                                                                                (0, 0.75, 0, 1), 5)
                else:
                    self.sender.addLineStripPoint(self.rightbz[self.surface_count], layout[x][y][z][0],
                                                  layout[x][y][z][1], "pix")
                ele = None
                if (z == 0) or (z == (len(layout[x][y]) - 1)):
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, "pix", (1, 0, 0, 0), 1,
                                                (1, 1, 0, 1), 10)
                else:
                    ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, "pix", (1, 0, 0, 0), 1,
                                                (0, 1, 0, 1), 10)
                self.rightCircles[self.surface_count].append(ele)
            self.bezierUpdates[self.surface_count] = [True, True, True, True]
            tlcoor = self.sender.getCirclePosition(self.topCircles[self.surface_count][0])
            trcoor = self.sender.getCirclePosition(
                self.topCircles[self.surface_count][len(self.topCircles[self.surface_count]) - 1])
            brcoor = self.sender.getCirclePosition(self.bottomCircles[self.surface_count][0])
            blcoor = self.sender.getCirclePosition(
                self.bottomCircles[self.surface_count][len(self.bottomCircles[self.surface_count]) - 1])
            center = self.line_intersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1], trcoor[0], trcoor[1], blcoor[0],
                                            blcoor[1])
            self.centerPoints[self.surface_count] = self.sender.newCircle(1, center[0], center[1], 10, "pix",
                                                                          (0, 0, 0, 0), 1, (1, 0, 1, 1), 10)
            self.surface_count += 1
            self.dontFlip[self.surface_count - 1] = True

    # Allows the user to define the four corners of a surface
    def define_surface(self):
        self.orientation[self.surface_count] = 0
        self.mirrored[self.surface_count] = False
        tl = None
        bl = None
        tr = None
        br = None

        self.topCircles[self.surface_count] = []
        self.bottomCircles[self.surface_count] = []
        self.leftCircles[self.surface_count] = []
        self.rightCircles[self.surface_count] = []
        self.bezierUpdates[self.surface_count] = [False, False, False, False]

        while not self.quit and tl is None and self.cursorMode == "wall":
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the top left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            tl = self.get_input(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        if not self.quit and self.cursorMode == "wall":
            self.topCircles[self.surface_count].append(tl[1])
            self.topbz[self.surface_count] = self.sender.newLineStrip(1, tl[0][0], tl[0][1], "pix", (0, 0.75, 0, 1), 5)
            self.hideable.append(self.topbz[self.surface_count])

        while not self.quit and tr is None and self.cursorMode == "wall":
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the top right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            tr = self.get_input(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        if not self.quit and self.cursorMode == "wall":
            self.topCircles[self.surface_count].append(tr[1])
            self.sender.addLineStripPoint(self.topbz[self.surface_count], tr[0][0], tr[0][1], "pix")
            self.rightCircles[self.surface_count].append(tr[1])
            self.rightbz[self.surface_count] = self.sender.newLineStrip(1, tr[0][0], tr[0][1], "pix", (0, 0.75, 0, 1),
                                                                        5)
            self.hideable.append(self.rightbz[self.surface_count])

        while not self.quit and br is None and self.cursorMode == "wall":
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the bottom right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            br = self.get_input(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        if not self.quit and self.cursorMode == "wall":
            self.rightCircles[self.surface_count].append(br[1])
            self.sender.addLineStripPoint(self.rightbz[self.surface_count], br[0][0], br[0][1], "pix")
            self.bottomCircles[self.surface_count].append(br[1])
            self.bottombz[self.surface_count] = self.sender.newLineStrip(1, br[0][0], br[0][1], "pix", (0, 0.75, 0, 1),
                                                                         5)
            self.hideable.append(self.bottombz[self.surface_count])

        while not self.quit and bl is None and self.cursorMode == "wall":
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the bottom left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            bl = self.get_input(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        if not self.quit and self.cursorMode == "wall":
            self.bottomCircles[self.surface_count].append(bl[1])
            self.sender.addLineStripPoint(self.bottombz[self.surface_count], bl[0][0], bl[0][1], "pix")
            self.leftCircles[self.surface_count].append(bl[1])
            self.leftbz[self.surface_count] = self.sender.newLineStrip(1, bl[0][0], bl[0][1], "pix", (0, 0.75, 0, 1),
                                                                       5)
            self.hideable.append(self.leftbz[self.surface_count])
            self.leftCircles[self.surface_count].append(tl[1])
            self.sender.addLineStripPoint(self.leftbz[self.surface_count], tl[0][0], tl[0][1], "pix")
            center = self.line_intersection(tl[0][0], tl[0][1], br[0][0], br[0][1], tr[0][0], tr[0][1], bl[0][0],
                                            bl[0][1])
            self.centerPoints[self.surface_count] = self.sender.newCircle(1, center[0], center[1], 10, "pix",
                                                                          (0, 0, 0, 0), 1, (1, 0, 1, 1), 10)
            self.surface_count += 1
            self.dontFlip[self.surface_count - 1] = True
        if self.cursorMode != "wall":
            self.orientation.pop(self.surface_count)
            self.mirrored.pop(self.surface_count)
            try:
                self.sender.removeElement(self.topbz[self.surface_count], 1)
                self.topbz.pop(self.surface_count)
            except:
                pass
            try:
                self.sender.removeElement(self.bottombz[self.surface_count], 1)
                self.bottombz.pop(self.surface_count)
            except:
                pass
            try:
                self.sender.removeElement(self.leftbz[self.surface_count], 1)
                self.leftbz.pop(self.surface_count)
            except:
                pass
            try:
                self.sender.removeElement(self.rightbz[self.surface_count], 1)
                self.rightbz.pop(self.surface_count)
            except:
                pass
            for x in range(0, len(self.topCircles[self.surface_count])):
                self.sender.removeElement(self.topCircles[self.surface_count][x], 1)
            self.topCircles.pop(self.surface_count)
            for x in range(0, len(self.bottomCircles[self.surface_count])):
                self.sender.removeElement(self.bottomCircles[self.surface_count][x], 1)
            self.bottomCircles.pop(self.surface_count)
            for x in range(0, len(self.leftCircles[self.surface_count])):
                self.sender.removeElement(self.leftCircles[self.surface_count][x], 1)
            self.leftCircles.pop(self.surface_count)
            for x in range(0, len(self.rightCircles[self.surface_count])):
                self.sender.removeElement(self.rightCircles[self.surface_count][x], 1)
            self.rightCircles.pop(self.surface_count)
            self.bezierUpdates.pop(self.surface_count)

    # looks through a data structure holding connections and draws connection lines as appropriate
    def visualize_connections(self, connections):
        for x in range(0, len(connections)):
            self.visualize_connection_lines((connections[x][0][0], connections[x][0][1]),
                                            (connections[x][1][0], connections[x][1][1]))

    # Creates both connection lines which indicate a connection between the two defined surface sides
    def visualize_connection_lines(self, from_side, to_side):
        self.create_connection_line((from_side[0], self.sideToCorners[from_side[1]][0]),
                                    (to_side[0], self.sideToCorners[to_side[1]][0]), True)
        self.create_connection_line((from_side[0], self.sideToCorners[from_side[1]][1]),
                                    (to_side[0], self.sideToCorners[to_side[1]][1]), True)

    def load_real_measurements(self, measurements):
        for x in range(0, len(measurements)):
            widstring = str(measurements[x][0])
            heistring = str(measurements[x][1])
            while len(widstring) < 4:
                widstring = "0" + widstring
            while len(heistring) < 4:
                heistring = "0" + heistring
            for y in range(0, 4):
                self.sender.setText(self.real_width_counter[x][y], widstring[y])
                self.sender.setText(self.real_height_counter[x][y], heistring[y])

    # topCounter
    # rightCounter
    # Quits the client
    def quit_button_handler(self):
        if not self.quit:
            for z in self.topCircles:
                for x in range(0, len(self.topCircles[z])):
                    self.sender.removeElement(self.topCircles[z][x], 1)
            for z in self.bottomCircles:
                for x in range(0, len(self.bottomCircles[z])):
                    self.sender.removeElement(self.bottomCircles[z][x], 1)
            for z in self.leftCircles:
                for x in range(0, len(self.leftCircles[z])):
                    self.sender.removeElement(self.leftCircles[z][x], 1)
            for z in self.rightCircles:
                for x in range(0, len(self.rightCircles[z])):
                    self.sender.removeElement(self.rightCircles[z][x], 1)
            for x in self.topbz:
                self.sender.removeElement(self.topbz[x], 1)
            for x in self.bottombz:
                self.sender.removeElement(self.bottombz[x], 1)
            for x in self.leftbz:
                self.sender.removeElement(self.leftbz[x], 1)
            for x in self.rightbz:
                self.sender.removeElement(self.rightbz[x], 1)
            for x in range(0, len(self.centerPoints)):
                self.sender.removeElement(self.centerPoints[x], 1)
            for x in range(0, len(self.warpedSurf)):
                self.sender.clearSurface(self.warpedSurf[x])

            self.sender.quitClientOnly()
            time.sleep(0.1)
            self.quit = True
            time.sleep(0.2)
            self.frame.quit()

    # Quits the client and server
    def quit_all_button_handler(self):
        if not self.quit:
            self.sender.quit()
            time.sleep(0.1)
            self.quit = True
            time.sleep(0.2)
            self.frame.quit()

    # Locks the mouse so that the server can be controlled
    def lock_mouse(self):
        self.mouseLock = True
        pygame.mouse.set_visible(False)
        self.sender.showCursor(self.mainCur)

    # Requests for the existing layout to be saved to a file
    def save_layout(self):
        if self.saveName.get() != "":
            hit = False
            confirm = False
            for x in range(0, self.loadList.size()):
                if self.loadList.get(x) == self.saveName.get():
                    hit = True
            if hit:
                confirm = tkMessageBox.askyesno("Overwrite",
                                                "Overwrite existing \"" + self.saveName.get() + "\" layout?")
            if not hit or confirm:
                self.sender.saveDefinedSurfaces(self.saveName.get())
                self.layouts = self.sender.getSavedLayouts()
                self.loadList.delete(0, END)
                for x in range(0, len(self.layouts)):
                    self.loadList.insert(END, self.layouts[x])
        else:
            tkMessageBox.showerror("Error", "Please enter save name first")

    # Requests for the currently selected layout to be loaded
    def load_layout(self):
        if len(self.loadList.curselection()) > 0:
            self.clear_visible_layout()
            count = self.sender.loadDefinedSurfaces(self.loadList.selection_get())
            self.redefine_surface(count[1])
            self.visualize_connections(count[2])
            self.load_real_measurements(count[3])
            self.update_rectangle(0)
            self.update_rectangle(1)
            self.update_rectangle(2)
            self.update_rectangle(3)
            self.saveName.delete(0, END)
            self.saveName.insert(0, self.loadList.selection_get())
        else:
            tkMessageBox.showerror("Error", "Please make a selection first")

    # Makes it so that the save filename matches the current selection in the layout list
    def select_list_entry_handler(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.saveName.delete(0, END)
        self.saveName.insert(0, value)

    # Refreshes the layout list by querying the server for an updated list
    def refresh_layouts_button_handler(self):
        self.layouts = self.sender.getSavedLayouts()
        self.loadList.delete(0, END)
        for x in range(0, len(self.layouts)):
            self.loadList.insert(END, self.layouts[x])

    # Ask the server to delete the layout that is currently selected in the layout list
    def delete_layout_button_handler(self):
        if len(self.loadList.curselection()) > 0:
            if self.loadList.selection_get() != "DEFAULT":
                self.sender.deleteLayout(self.loadList.selection_get())
                self.layouts = self.sender.getSavedLayouts()
                self.loadList.delete(0, END)
                for x in range(0, len(self.layouts)):
                    self.loadList.insert(END, self.layouts[x])
            else:
                tkMessageBox.showinfo("Error", "You are not allowed to delete the \"DEFAULT\" layout")
        else:
            tkMessageBox.showerror("Error", "Please make a selection first")

    # Clear the currently defined layout on both the client and server side
    def clear_visible_layout(self):
        time.sleep(3)
        self.sender.undefineSurface(self.warpedSurf[0])
        self.sender.undefineSurface(self.warpedSurf[1])
        self.sender.undefineSurface(self.warpedSurf[2])
        self.sender.undefineSurface(self.warpedSurf[3])
        for z in self.topCircles:
            for x in range(0, len(self.topCircles[z])):
                self.sender.removeElement(self.topCircles[z][x], 1)
        self.topCircles = {}
        for z in self.bottomCircles:
            for x in range(0, len(self.bottomCircles[z])):
                self.sender.removeElement(self.bottomCircles[z][x], 1)
        self.bottomCircles = {}
        for z in self.leftCircles:
            for x in range(0, len(self.leftCircles[z])):
                self.sender.removeElement(self.leftCircles[z][x], 1)
        self.leftCircles = {}
        for z in self.rightCircles:
            for x in range(0, len(self.rightCircles[z])):
                self.sender.removeElement(self.rightCircles[z][x], 1)
        self.rightCircles = {}
        for x in self.topbz:
            self.sender.removeElement(self.topbz[x], 1)
        self.topbz = {}
        for x in self.bottombz:
            self.sender.removeElement(self.bottombz[x], 1)
        self.bottombz = {}
        for x in self.leftbz:
            self.sender.removeElement(self.leftbz[x], 1)
        self.leftbz = {}
        for x in self.rightbz:
            self.sender.removeElement(self.rightbz[x], 1)
        self.rightbz = {}
        for x in self.mirrored:
            self.mirrored[x] = False
        for x in self.orientation:
            self.orientation[x] = 0

        for x in range(0, len(self.centerPoints)):
            self.sender.removeElement(self.centerPoints[x], 1)
        self.centerPoints = {}

        for x in list(reversed(range(0, len(self.connections)))):
            self.create_connection_line(self.connections[x][0], self.connections[x][1], False)

        self.surface_count = 0

        self.saveName.delete(0, END)
        self.saveName.insert(0, "")

    # Defines the GUI
    def tkinter_thread(self):
        self.master = Tk()
        self.master.wm_title("Configuration GUI")
        self.frame = Frame(self.master)
        self.frame.pack()
        self.frame2 = Frame(self.master)
        self.frame2.pack()
        self.frame3 = Frame(self.master)
        self.frame3.pack()
        self.frame4 = Frame(self.master)
        self.frame4.pack()
        self.frame5 = Frame(self.master)
        self.frame5.pack()
        self.frame6 = Frame(self.master)
        self.frame6.pack()
        self.frame7 = Frame(self.master)
        self.frame7.pack()
        self.frame8 = Frame(self.master)
        self.frame8.pack()
        self.frame9 = Frame(self.master)
        self.frame9.pack()
        self.frame10 = Frame(self.master)
        self.frame10.pack()
        self.frame11 = Frame(self.master)
        self.frame11.pack()
        self.frame12 = Frame(self.master)
        self.frame12.pack()
        self.button = Button(self.frame, text="QUIT CLIENT", fg="red", command=self.quit_button_handler, width=40)
        self.button.pack(side=LEFT)
        self.slogan = Button(self.frame2, text="Control Projected Mouse (Middle Click to Release)",
                             command=self.lock_mouse, width=40)
        self.slogan.pack(side=LEFT)
        self.label = Label(self.frame3, text="Save name", width=10)
        self.label.pack(side=LEFT)
        self.saveName = Entry(self.frame3, width=32)
        self.saveName.pack(side=LEFT)
        self.saveBut = Button(self.frame4, text="Save Layout", command=self.save_layout, width=40)
        self.saveBut.pack(side=LEFT)
        self.label = Label(self.frame5, text="-- Saved Layouts --", width=40, height=2)
        self.label.pack(side=LEFT)
        layout_scrollbar = Scrollbar(self.frame6, orient=VERTICAL)
        self.loadList = Listbox(self.frame6, width=41, yscrollcommand=layout_scrollbar.set)
        layout_scrollbar.config(command=self.loadList.yview)
        layout_scrollbar.pack(side=RIGHT, fill=Y)
        self.loadList.pack(side=LEFT, fill=BOTH, expand=1)
        layouts = self.sender.getSavedLayouts()
        index = 0
        for x in range(0, len(layouts)):
            if layouts[x] == "DEFAULT":
                index = x
            self.loadList.insert(END, layouts[x])
        self.loadList.bind('<<ListboxSelect>>', self.select_list_entry_handler)
        self.loadList.select_set(index)
        self.load_layout()
        self.saveBut = Button(self.frame7, text="Load Layout", command=self.load_layout, width=18)
        self.saveBut.pack(side=LEFT)
        self.saveBut = Button(self.frame7, text="Refresh List", command=self.refresh_layouts_button_handler, width=18)
        self.saveBut.pack(side=LEFT)
        self.saveBut = Button(self.frame8, text="Delete Layout", command=self.delete_layout_button_handler, width=18)
        self.saveBut.pack(side=LEFT)
        self.saveBut = Button(self.frame8, text="Clear Current Layout", command=self.clear_visible_layout, width=18)
        self.saveBut.pack(side=LEFT)
        self.master.mainloop()

    # Sets up the surfaces which can be defined within the client
    def init_gui(self):
        self.sender.showSetupSurface()
        self.sender.newCanvas(0, 0, 1024, 1280, 1024, "pix", "setupCanvas")
        self.mainCur = self.sender.newCursor(0, 1280 / 2, 1024 / 2, "pix")

        self.controlCur = self.mainCur

        self.sender.hideCursor(self.mainCur)

        self.warpedSurf[0] = self.sender.newSurface()
        self.canvas = self.sender.newCanvas(self.warpedSurf[0], 0, 512, 512, 512, "pix", "Bob")
        self.surfCur[0] = self.sender.newCursor(self.warpedSurf[0], 512 / 2, 512 / 2, "pix")
        self.sender.hideCursor(self.surfCur[0])
        self.texRects[0] = self.sender.newTexRectangle(self.canvas, 0, 512, 512, 512, "pix", "checks.jpg")
        self.stretchRects[0] = self.sender.newRectangle(self.canvas, 512 / 2 - 75, 512 / 2 + 75, 150, 150, "pix",
                                                        (0, 0, 0, 0), 1, (0, 0, 1, 1))
        self.centSurfCirc[0] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2, 25, "pix", (0, 0, 0, 0), 0,
                                                     (1, 1, 0, 1), 10)
        self.sender.hideElement(self.centSurfCirc[0])
        self.sender.hideElement(self.stretchRects[0])
        surface_aspect_stretch_circles = {}
        surface_aspect_stretch_circles[0] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 + 75, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[0])
        surface_aspect_stretch_circles[1] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 - 75, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[1])
        surface_aspect_stretch_circles[2] = self.sender.newCircle(self.canvas, 512 / 2 - 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[2])
        surface_aspect_stretch_circles[3] = self.sender.newCircle(self.canvas, 512 / 2 + 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[3])

        self.real_width_rect[0] = self.sender.newRectangle(self.canvas, 512 / 2 - 80, 512, 160, 75, "pix", (0, 0, 0, 0),
                                                           0,
                                                           (1, 1, 1, 1))
        width_digit_1 = self.sender.newText(self.canvas, "0", 512 / 2 - 75, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_2 = self.sender.newText(self.canvas, "0", 512 / 2 - 50, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_3 = self.sender.newText(self.canvas, "0", 512 / 2 - 25, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_4 = self.sender.newText(self.canvas, "0", 512 / 2, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        self.real_width_counter[0] = (width_digit_1, width_digit_2, width_digit_3, width_digit_4)
        self.real_width_unit[0] = self.sender.newText(self.canvas, "cm", 512 / 2 + 25, 460, "pix", 35, "Arial",
                                                      (0, 0, 0, 1))

        self.real_height_rect[0] = self.sender.newRectangle(self.canvas, 512 - 180, 512 / 2 + 30, 180, 60, "pix",
                                                            (0, 0, 0, 0), 0, (1, 1, 1, 1))
        height_digit_1 = self.sender.newText(self.canvas, "0", 512 - 175, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_2 = self.sender.newText(self.canvas, "0", 512 - 150, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_3 = self.sender.newText(self.canvas, "0", 512 - 125, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_4 = self.sender.newText(self.canvas, "0", 512 - 100, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        self.real_height_counter[0] = (height_digit_1, height_digit_2, height_digit_3, height_digit_4)
        self.real_height_unit[0] = self.sender.newText(self.canvas, "cm", 512 - 65, 512 / 2 - 13, "pix", 35, "Arial",
                                                       (0, 0, 0, 1))
        self.aspect_stretch_circles[0] = surface_aspect_stretch_circles
        self.surfCanvases[0] = self.canvas

        self.warpedSurf[1] = self.sender.newSurface()
        self.canvas = self.sender.newCanvas(self.warpedSurf[1], 0, 512, 512, 512, "pix", "Bob")
        self.surfCur[1] = self.sender.newCursor(self.warpedSurf[1], 512 / 2, 512 / 2, "pix")
        self.sender.hideCursor(self.surfCur[1])
        self.texRects[1] = self.sender.newTexRectangle(self.canvas, 0, 512, 512, 512, "pix", "checks.jpg")
        self.stretchRects[1] = self.sender.newRectangle(self.canvas, 512 / 2 - 75, 512 / 2 + 75, 150, 150, "pix",
                                                        (0, 0, 0, 0), 1, (0, 0, 1, 1))
        self.centSurfCirc[1] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2, 25, "pix", (0, 0, 0, 0), 0,
                                                     (1, 1, 0, 1), 10)
        self.sender.hideElement(self.centSurfCirc[1])
        self.sender.hideElement(self.stretchRects[1])
        surface_aspect_stretch_circles = {}
        surface_aspect_stretch_circles[0] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 + 75, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[0])
        surface_aspect_stretch_circles[1] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 - 75, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[1])
        surface_aspect_stretch_circles[2] = self.sender.newCircle(self.canvas, 512 / 2 - 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[2])
        surface_aspect_stretch_circles[3] = self.sender.newCircle(self.canvas, 512 / 2 + 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1),
                                                                  10)
        self.sender.hideElement(surface_aspect_stretch_circles[3])
        self.real_width_rect[1] = self.sender.newRectangle(self.canvas, 512 / 2 - 80, 512, 160, 75, "pix", (0, 0, 0, 0),
                                                           0,
                                                           (1, 1, 1, 1))
        width_digit_1 = self.sender.newText(self.canvas, "0", 512 / 2 - 75, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_2 = self.sender.newText(self.canvas, "0", 512 / 2 - 50, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_3 = self.sender.newText(self.canvas, "0", 512 / 2 - 25, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_4 = self.sender.newText(self.canvas, "0", 512 / 2, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        self.real_width_counter[1] = (width_digit_1, width_digit_2, width_digit_3, width_digit_4)
        self.real_width_unit[1] = self.sender.newText(self.canvas, "cm", 512 / 2 + 25, 460, "pix", 35, "Arial",
                                                      (0, 0, 0, 1))
        self.real_height_rect[1] = self.sender.newRectangle(self.canvas, 512 - 180, 512 / 2 + 30, 180, 60, "pix",
                                                            (0, 0, 0, 0), 0, (1, 1, 1, 1))
        height_digit_1 = self.sender.newText(self.canvas, "0", 512 - 175, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_2 = self.sender.newText(self.canvas, "0", 512 - 150, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_3 = self.sender.newText(self.canvas, "0", 512 - 125, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_4 = self.sender.newText(self.canvas, "0", 512 - 100, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        self.real_height_counter[1] = (height_digit_1, height_digit_2, height_digit_3, height_digit_4)
        self.real_height_unit[1] = self.sender.newText(self.canvas, "cm", 512 - 65, 512 / 2 - 13, "pix", 35, "Arial",
                                                       (0, 0, 0, 1))
        self.aspect_stretch_circles[1] = surface_aspect_stretch_circles
        self.surfCanvases[1] = self.canvas

        self.warpedSurf[2] = self.sender.newSurface()
        self.canvas = self.sender.newCanvas(self.warpedSurf[2], 0, 512, 512, 512, "pix", "Bob")
        self.surfCur[2] = self.sender.newCursor(self.warpedSurf[2], 512 / 2, 512 / 2, "pix")
        self.sender.hideCursor(self.surfCur[2])
        self.texRects[2] = self.sender.newTexRectangle(self.canvas, 0, 512, 512, 512, "pix", "checks.jpg")
        self.stretchRects[2] = self.sender.newRectangle(self.canvas, 512 / 2 - 75, 512 / 2 + 75, 150, 150, "pix",
                                                        (0, 0, 0, 0), 1, (0, 0, 1, 1))
        self.centSurfCirc[2] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2, 25, "pix", (0, 0, 0, 0), 0,
                                                     (1, 1, 0, 1), 10)
        self.sender.hideElement(self.centSurfCirc[2])
        self.sender.hideElement(self.stretchRects[2])
        surface_aspect_stretch_circles = {}
        surface_aspect_stretch_circles[0] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 + 75, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[0])
        surface_aspect_stretch_circles[1] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 - 75, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[1])
        surface_aspect_stretch_circles[2] = self.sender.newCircle(self.canvas, 512 / 2 - 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[2])
        surface_aspect_stretch_circles[3] = self.sender.newCircle(self.canvas, 512 / 2 + 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0),
                                                                  1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[3])
        self.real_width_rect[2] = self.sender.newRectangle(self.canvas, 512 / 2 - 80, 512, 160, 75, "pix", (0, 0, 0, 0),
                                                           0,
                                                           (1, 1, 1, 1))
        width_digit_1 = self.sender.newText(self.canvas, "0", 512 / 2 - 75, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_2 = self.sender.newText(self.canvas, "0", 512 / 2 - 50, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_3 = self.sender.newText(self.canvas, "0", 512 / 2 - 25, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_4 = self.sender.newText(self.canvas, "0", 512 / 2, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        self.real_width_counter[2] = (width_digit_1, width_digit_2, width_digit_3, width_digit_4)
        self.real_width_unit[2] = self.sender.newText(self.canvas, "cm", 512 / 2 + 25, 460, "pix", 35, "Arial",
                                                      (0, 0, 0, 1))
        self.real_height_rect[2] = self.sender.newRectangle(self.canvas, 512 - 180, 512 / 2 + 30, 180, 60, "pix",
                                                            (0, 0, 0, 0), 0, (1, 1, 1, 1))
        height_digit_1 = self.sender.newText(self.canvas, "0", 512 - 175, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_2 = self.sender.newText(self.canvas, "0", 512 - 150, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_3 = self.sender.newText(self.canvas, "0", 512 - 125, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_4 = self.sender.newText(self.canvas, "0", 512 - 100, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        self.real_height_counter[2] = (height_digit_1, height_digit_2, height_digit_3, height_digit_4)
        self.real_height_unit[2] = self.sender.newText(self.canvas, "cm", 512 - 65, 512 / 2 - 13, "pix", 35, "Arial",
                                                       (0, 0, 0, 1))
        self.aspect_stretch_circles[2] = surface_aspect_stretch_circles
        self.surfCanvases[2] = self.canvas

        self.warpedSurf[3] = self.sender.newSurface()
        self.canvas = self.sender.newCanvas(self.warpedSurf[3], 0, 512, 512, 512, "pix", "Bob")
        self.surfCur[3] = self.sender.newCursor(self.warpedSurf[3], 512 / 2, 512 / 2, "pix")
        self.sender.hideCursor(self.surfCur[3])
        self.texRects[3] = self.sender.newTexRectangle(self.canvas, 0, 512, 512, 512, "pix", "checks.jpg")
        self.stretchRects[3] = self.sender.newRectangle(self.canvas, 512 / 2 - 75, 512 / 2 + 75, 150, 150, "pix",
                                                        (0, 0, 0, 0), 1, (0, 0, 1, 1))
        self.centSurfCirc[3] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2, 25, "pix", (0, 0, 0, 0), 0,
                                                     (1, 1, 0, 1), 10)
        self.sender.hideElement(self.centSurfCirc[3])
        self.sender.hideElement(self.stretchRects[3])
        surface_aspect_stretch_circles = {}
        surface_aspect_stretch_circles[0] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 + 75, 15, "pix",
                                                                  (0, 0, 0, 0), 1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[0])
        surface_aspect_stretch_circles[1] = self.sender.newCircle(self.canvas, 512 / 2, 512 / 2 - 75, 15, "pix",
                                                                  (0, 0, 0, 0), 1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[1])
        surface_aspect_stretch_circles[2] = self.sender.newCircle(self.canvas, 512 / 2 - 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0), 1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[2])
        surface_aspect_stretch_circles[3] = self.sender.newCircle(self.canvas, 512 / 2 + 75, 512 / 2, 15, "pix",
                                                                  (0, 0, 0, 0), 1, (0, 1, 0, 1), 10)
        self.sender.hideElement(surface_aspect_stretch_circles[3])
        self.real_width_rect[3] = self.sender.newRectangle(self.canvas, 512 / 2 - 80, 512, 160, 75, "pix", (0, 0, 0, 0),
                                                           0, (1, 1, 1, 1))
        width_digit_1 = self.sender.newText(self.canvas, "0", 512 / 2 - 75, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_2 = self.sender.newText(self.canvas, "0", 512 / 2 - 50, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_3 = self.sender.newText(self.canvas, "0", 512 / 2 - 25, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        width_digit_4 = self.sender.newText(self.canvas, "0", 512 / 2, 460, "pix", 37, "Arial", (0, 0, 0, 1))
        self.real_width_counter[3] = (width_digit_1, width_digit_2, width_digit_3, width_digit_4)
        self.real_width_unit[3] = self.sender.newText(self.canvas, "cm", 512 / 2 + 25, 460, "pix", 35, "Arial",
                                                      (0, 0, 0, 1))

        self.real_height_rect[3] = self.sender.newRectangle(self.canvas, 512 - 180, 512 / 2 + 30, 180, 60, "pix",
                                                            (0, 0, 0, 0), 0, (1, 1, 1, 1))
        height_digit_1 = self.sender.newText(self.canvas, "0", 512 - 175, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_2 = self.sender.newText(self.canvas, "0", 512 - 150, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_3 = self.sender.newText(self.canvas, "0", 512 - 125, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        height_digit_4 = self.sender.newText(self.canvas, "0", 512 - 100, 512 / 2 - 13, "pix", 37, "Arial",
                                             (0, 0, 0, 1))
        self.real_height_counter[3] = (height_digit_1, height_digit_2, height_digit_3, height_digit_4)
        self.real_height_unit[3] = self.sender.newText(self.canvas, "cm", 512 - 65, 512 / 2 - 13, "pix", 35, "Arial",
                                                       (0, 0, 0, 1))
        self.aspect_stretch_circles[3] = surface_aspect_stretch_circles
        self.surfCanvases[3] = self.canvas

        self.surface_count = 0

    # The main loop
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        self.ppe = parser.getint('RoomSetup', 'PointsPerEdge')
        self.refreshrate = 1 / (parser.getint('library', 'MovesPerSecond'))
        self.sender = messageSender()
        self.winWidth = 320
        self.winHeight = 240

        # Initialise screen
        pygame.init()
        self.screen = pygame.display.set_mode((self.winWidth, self.winHeight))
        pygame.display.set_caption('Room setup program')

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

        self.sender.login("jp438")
        self.sender.setapp("myapp")

        tk_thread = threading.Thread(target=self.tkinter_thread, args=())  # Creates the display thread
        tk_thread.start()  # Starts the display thread

        self.layouts = self.sender.getSavedLayouts()
        self.init_gui()

        self.mouseLock = False
        pygame.mouse.set_visible(True)

        mouse_thread = threading.Thread(target=self.mouse_movement, args=())  # Creates the display thread
        mouse_thread.start()  # Starts the display thread

        if not self.quit:
            thread = threading.Thread(target=self.bezier_update_tracker, args=())  # Creates the display thread
            thread.start()  # Starts the display thread
            while not self.quit:
                self.background.fill((255, 255, 255))
                text = self.font.render("", 1, (10, 10, 10))
                text_position = text.get_rect()
                text_position.centerx = self.background.get_rect().centerx
                self.background.blit(text, text_position)
                self.get_input(False)
                self.screen.blit(self.background, (0, 0))
                pygame.display.flip()
                time.sleep(1.0 / 60)
        time.sleep(0.2)
        pygame.quit()


Client()
