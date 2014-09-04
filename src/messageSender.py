import socket, sys, select, time, threading
from ConfigParser import SafeConfigParser

class messageSender:
    __slots__ = ['s', 'host', 'port', 'refreshrate']
    sending = 0
    ERRORS = {1 : "Invalid API call",
              2 : "Wrong number of arguments (% instead of %)",
              3 : "User name not yet set",
              4 : "User name already set",
              5 : "Application name already set",
              6 : "Application name not yet set",
              7 : "Must be owner to change admin setting"
    }
    elelocs = {} #Could act as cache inside bus in future versions (to allow multiple clients)
    eletrack = {}
    stripLock = threading.Lock()
    sendlock = threading.Lock()
    
    def eleUpdater(self):
        while True:
            #print str(self.eletrack)
            strips = 0
            for x in range(1,len(self.elelocs)+1):
                if(self.eletrack[x][0] == True):
                    if(self.eletrack[x][1] == "lineStrip"):
                        strips += 1
                        self.stripLock.acquire()
                        converted = str(self.elelocs[x][0][0]) + ":" + str(self.elelocs[x][0][1])
                        for y in range(0,len(self.elelocs[x])):
                            converted += ";" + str(self.elelocs[x][y][0]) + ":" + str(self.elelocs[x][y][1])
                        self.sendMessage("set_line_strip_content," + str(x) + "," + converted)
                        self.stripLock.release()
                    elif(self.eletrack[x][1] == "circle"):
                        self.sendMessage("relocate_circle," + str(x) + "," + str(self.elelocs[x][0]) + "," + str(self.elelocs[x][1]))
                    self.eletrack[x][0]=False
            time.sleep(self.refreshrate)
    
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        self.refreshrate = 1/(parser.getint('library','MovesPerSecond'))
        self.host = parser.get('connection','host')
        self.port = parser.getint('connection','port')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(2)
        thread = threading.Thread(target=self.eleUpdater, args=()) #Creates the display thread
        thread.start() #Starts the display thread
        try:
            self.s.connect((self.host,self.port))
        except:
            print 'Unable to connect'
            sys.exit()
            
        print 'Connected to remote host. Start sending messages'
        
    def colorString(self, red, green, blue, alpha):
        return str(red) + ":" + str(green) + ":" + str(blue) + ":" + str(alpha)
        
    def sendMessage(self, message):
        self.sendlock.acquire()
        self.sending+=1
        #print "Sending " + str(self.sending)
        self.s.send(message)
        if(message=="quit"):
            print '\033[1;31mShutting down client\033[1;m'
            sys.exit(0)
        socket_list = [sys.stdin, self.s]
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
        
        for sock in read_sockets:
            data = sock.recv(4096)
            if not data:
                print '\nDisconnected from server'
                sys.exit()
            else:
                dict = eval(data)
                try:
                    errno = dict["error"]
                    error = str(self.ERRORS[errno])
                    spliterr = error.split("%")
                    errorStr = spliterr[0]
                    for x in range(1,len(spliterr)):
                        errorStr = errorStr + dict[str(x)] + spliterr[x]
                    print "\033[1;31mERROR: " + errorStr + "\033[1;m"
                    self.sendlock.release()
                    return dict
                except:
                    self.sendlock.release()
                    return dict
                
    def quit(self):
        self.sendMessage("quit")
        
    def login(self, username):
        self.sendMessage("login," + str(username))
        
    def setapp(self, appname):
        self.sendMessage("setapp," + str(appname))
    
    def newSurface(self):
        sur = self.sendMessage("new_surface")
        surNo = int(sur["surfaceNo"])
        return surNo
        
    def newSurfaceWithID(self, ID):
        return self.sendMessage("new_surface_with_ID," + str(ID))
    
    def newCursor(self, surfaceNo, x, y):
        cur = self.sendMessage("new_cursor," + str(surfaceNo) + "," + str(x) + "," + str(y))
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newCursorWithID(self, ID, surfaceNo, x, y):
        cur = self.sendMessage("new_cursor_with_ID," + str(ID) + "," + str(surfaceNo) + "," + str(x) + "," + str(y))
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newWindow(self, surfaceNo, x, y, width, height, name):
        win = self.sendMessage("new_window," + str(surfaceNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + name)
        winNo = int(win["windowNo"])
        return winNo
    
    def newWindowWithID(self, ID, surfaceNo, x, y, width, height, name):
        win = self.sendMessage("new_window_with_ID," + str(ID) + "," + str(surfaceNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + name)
        winNo = int(win["windowNo"])
        return winNo
    
    def newCircle(self, windowNo, x, y, radius, lineCol, fillCol, sides):
        ele = self.sendMessage("new_circle," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(radius) + "," + self.colorString(lineCol[0], lineCol[1], lineCol[2], lineCol[3]) + "," + self.colorString(fillCol[0], fillCol[1], fillCol[2], fillCol[3]) + "," + str(sides))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"circle"]
        return eleNo
    
    def newCircleWithID(self, ID, windowNo, x, y, radius, lineCol, fillCol, sides):
        ele = self.sendMessage("new_circle_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(radius) + "," + self.colorString(lineCol[0], lineCol[1], lineCol[2], lineCol[3]) + "," + self.colorString(fillCol[0], fillCol[1], fillCol[2], fillCol[3]) + "," + str(sides))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"circle"]
        return eleNo
    
    def newLine(self, windowNo, xStart, yStart, xEnd, yEnd, color, width):
        ele = self.sendMessage("new_line," + str(windowNo) + "," + str(xStart) + "," + str(yStart) + "," + str(xEnd) + "," + str(yEnd) + "," + self.colorString(color[0], color[1], color[2], color[3]) + "," + str(width))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (xStart,yStart,xEnd,yEnd)
        self.eletrack[eleNo] = [True,"line"]
        return eleNo
    
    def newLineWithID(self, ID, windowNo, xStart, yStart, xEnd, yEnd, color, width):
        ele = self.sendMessage("new_line_with_ID," + str(ID) + "," + str(windowNo) + "," + str(xStart) + "," + str(yStart) + "," + str(xEnd) + "," + str(yEnd) + "," + self.colorString(color[0], color[1], color[2], color[3]) + "," + str(width))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (xStart,yStart,xEnd,yEnd)
        self.eletrack[eleNo] = [True,"line"]
        return eleNo
    
    def newLineStrip(self, windowNo, x, y, color, width):
        ele = self.sendMessage("new_line_strip," + str(windowNo) + "," + str(x) + "," + str(y) + "," + self.colorString(color[0], color[1], color[2], color[3]) + "," + str(width))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"lineStrip"]
        return eleNo
    
    def newLineStripWithID(self, ID, windowNo, x, y, color, width):
        ele = self.sendMessage("new_line_strip_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + self.colorString(color[0], color[1], color[2], color[3]) + "," + str(width))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"lineStrip"]
        return eleNo
    
    def newPolygon(self, windowNo, x, y, lineColor, fillColor):
        ele = self.sendMessage("new_polygon," + str(windowNo) + "," + str(x) + "," + str(y) + "," + self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]) + "," + self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3]))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"polygon"]
        return eleNo
    
    def newPolygonWithID(self, ID, windowNo, x, y, lineColor, fillColor):
        ele = self.sendMessage("new_polygon_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]) + "," + self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3]))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"polygon"]
        return eleNo
    
    def newTexRectangle(self, windowNo, x, y, width, height, texture):
        ele = self.sendMessage("new_texrectangle," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + str(texture))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"texrectangle"]
        return eleNo
    
    def newTexRectangleWithID(self, ID, windowNo, x, y, width, height, texture):
        ele = self.sendMessage("new_texrectangle_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + str(texture))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"texrectangle"]
        return eleNo
    
    def newRectangle(self, windowNo, x, y, width, height, lineColor, fillColor):
        ele = self.sendMessage("new_rectangle," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]) + "," + self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3]))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"rectangle"]
        return eleNo
    
    def newRectangleWithID(self, ID, windowNo, x, y, width, height, lineColor, fillColor):
        ele = self.sendMessage("new_rectangle_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]) + "," + self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3]))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"rectangle"]
        return eleNo
    
    def newText(self, windowNo, text, x, y, ptSize, font, color):
        ele = self.sendMessage("new_text," + str(windowNo) + "," + text + "," + str(x) + "," + str(y) + "," + str(ptSize) + "," + font + "," + self.colorString(color[0], color[1], color[2], color[3]))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"text"]
        return eleNo
    
    def newTextWithID(self, ID, windowNo, text, x, y, ptSize, font, color):
        ele = self.sendMessage("new_text_with_ID," + str(ID) + "," + str(windowNo) + "," + text + "," + str(x) + "," + str(y) + "," + str(ptSize) + "," + font + "," + self.colorString(color[0], color[1], color[2], color[3]))
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"text"]
        return eleNo
    
    def subscribeToSurface(self, surfaceNo):
        self.sendMessage("subscribe_to_surface," + str(surfaceNo))
    
    def getSurfaceID(self, surfaceNo):
        ID = self.sendMessage("get_surface_ID," + str(surfaceNo))
        return ID["ID"]
    
    def setSurfaceID(self, surfaceNo, ID):
        self.sendMessage("set_surface_ID," + str(surfaceNo) + "," + str(ID))
    
    def getSurfaceOwner(self, surfaceNo):
        owner = self.sendMessage("get_surface_owner," + str(surfaceNo))
        return owner["owner"]
        
    def getSurfaceAppDetails(self, surfaceNo):
        details = self.sendMessage("get_surface_app_details," + str(surfaceNo))
        return (details["app"],details["instance"])
        
    def getSurfacesByID(self, ID):
        surfaces = self.sendMessage("get_surfaces_by_ID," + str(ID))
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByOwner(self, owner):
        surfaces = self.sendMessage("get_surfaces_by_owner," + str(owner))
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByAppName(self, name):
        surfaces = self.sendMessage("get_surfaces_by_app_name," +  str(name))
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByAppDetails(self, name, instance):
        surfaces = self.sendMessage("get_surfaces_by_app_details" + str(name) + "," + str(instance))
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def becomeSurfaceAdmin(self, surfaceNo):
        self.sendMessage("become_surface_admin," + str(surfaceNo))
        
    def stopBeingSurfaceAdmin(self, surfaceNo):
        self.sendMessage("stop_being_surface_admin," + str(surfaceNo))
        
    def setSurfaceEdges(self, surfaceNo, topPoints, bottomPoints, leftPoints, rightPoints):
        topString = str(topPoints[0][0]) + ":" + str(topPoints[0][1])
        bottomString = str(bottomPoints[0][0]) + ":" + str(bottomPoints[0][1])
        leftString = str(leftPoints[0][0]) + ":" + str(leftPoints[0][1])
        rightString = str(rightPoints[0][0]) + ":" + str(rightPoints[0][1])
        for x in range(1,len(topPoints)):
            topString += (";" + str(topPoints[x][0]) + ":" + str(topPoints[x][1]))
        for x in range(1,len(bottomPoints)):
            bottomString += (";" + str(bottomPoints[x][0]) + ":" + str(bottomPoints[x][1]))
        for x in range(1,len(leftPoints)):
            leftString += (";" + str(leftPoints[x][0]) + ":" + str(leftPoints[x][1]))
        for x in range(1,len(rightPoints)):
            rightString += (";" + str(rightPoints[x][0]) + ":" + str(rightPoints[x][1]))
        self.sendMessage("set_surface_edges," + str(surfaceNo) + "," + topString + "," + bottomString + "," + leftString + "," + rightString)
        
    def undefineSurface(self, surfaceNo):
        self.sendMessage("undefine_surface")
        
    def subscribeToWindow(self, windowNo):
        self.sendMessage("subscribe_to_window," + str(windowNo))
        
    def getWindowID(self, windowNo):
        ID = self.sendMessage("get_window_ID," + str(windowNo))
        return ID["ID"]
    
    def setWindowID(self, windowNo, ID):
        self.sendMessage("set_window_ID," + str(windowNo) + "," + str(ID))
    
    def getWindowOwner(self, windowNo):
        owner = self.sendMessage("get_window_owner," + str(windowNo))
        return owner["owner"]
        
    def getWindowAppDetails(self, surfaceNo):
        details = self.sendMessage("get_window_app_details," + str(surfaceNo))
        return (details["app"],details["instance"])
        
    def getWindowsByID(self, ID):
        windows = self.sendMessage("get_windows_by_ID," + str(ID))
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def getWindowsByOwner(self, owner):
        windows = self.sendMessage("get_windows_by_owner," + str(owner))
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def getWindowsByAppName(self, name):
        windows = self.sendMessage("get_windows_by_app_name," +  str(name))
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def getWindowssByAppDetails(self, name, instance):
        windows = self.sendMessage("get_windows_by_app_details" + str(name) + "," + str(instance))
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def becomeWindowAdmin(self, windowNo):
        self.sendMessage("become_window_admin," + str(windowNo))
        
    def stopBeingWindowAdmin(self, windowNo):
        self.sendMessage("stop_being_window_admin," + str(windowNo))
        
    def subscribeToElement(self, elementNo):
        self.sendMessage("subscribe_to_element," + str(elementNo))
        
    def getElementID(self, elementNo):
        ID = self.sendMessage("get_element_ID," + str(elementNo))
        return ID["ID"]
    
    def setElementID(self, elementNo, ID):
        self.sendMessage("set_element_ID," + str(elementNo) + "," + str(ID))
    
    def getElementOwner(self, elementNo):
        owner = self.sendMessage("get_element_owner," + str(elementNo))
        return owner["owner"]
        
    def getElementAppDetails(self, surfaceNo):
        details = self.sendMessage("get_element_app_details," + str(surfaceNo))
        return (details["app"],details["instance"])
        
    def getElementsByID(self, ID):
        elements = self.sendMessage("get_elements_by_ID," + str(ID))
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByOwner(self, owner):
        elements = self.sendMessage("get_elements_by_owner," + str(owner))
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByAppName(self, name):
        elements = self.sendMessage("get_elements_by_app_name," +  str(name))
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByAppDetails(self, name, instance):
        elements = self.sendMessage("get_elements_by_app_details," + str(name) + "," + str(instance))
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
    
    def getElementsOnWindow(self, surfaceNo):
        elements = self.sendMessage("get_elements_on_window," + str(surfaceNo))
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def becomeElementAdmin(self, elementNo):
        self.sendMessage("become_element_admin," + str(elementNo))
        
    def stopBeingElementAdmin(self, elementNo):
        self.sendMessage("stop_being_element_admin," + str(elementNo))
    
    def mouseLeftDown(self, cursorNo):
        pt = self.sendMessage("mouse_l," + str(cursorNo))
        return (pt["x"],pt["y"])
    
    def mouseLeftUp(self, cursorNo):
        pt = self.sendMessage("mouse_lu," + str(cursorNo))
        return (pt["x"],pt["y"],pt["duration"])
    
    def mouseMiddleDown(self, cursorNo):
        pt = self.sendMessage("mouse_m," + str(cursorNo))
        return (pt["x"],pt["y"])
    
    def mouseMiddleUp(self, cursorNo):
        pt = self.sendMessage("mouse_mu," + str(cursorNo))
        return (pt["x"],pt["y"],pt["duration"])
    
    def mouseRightDown(self, cursorNo):
        pt = self.sendMessage("mouse_r," + str(cursorNo))
        return (pt["x"],pt["y"])
    
    def mouseRightUp(self, cursorNo):
        pt = self.sendMessage("mouse_ru," + str(cursorNo))
        return (pt["x"],pt["y"],pt["duration"])
    
    def moveCursor(self, cursorNo, xDistance, yDistance):
        self.sendMessage("move_cursor," + str(cursorNo) + "," + str(xDistance) + "," + str(yDistance))
        
    def testMoveCursor(self, cursorNo, xDistance, yDistance):
        loc = self.sendMessage("test_move_cursor," + str(cursorNo) + "," + str(xDistance) + "," + str(yDistance))
        return [loc["x"],loc["y"]]
    
    def relocateCursor(self, cursorNo, x, y, surfaceNo):
        self.sendMessage("relocate_cursor," + str(cursorNo) + "," + str(x) + "," + str(y) + "," + str(surfaceNo))
    
    def getCursorPosition(self, cursorNo):
        loc = self.sendMessage("get_cursor_pos," + str(cursorNo))
        return [loc["x"],loc["y"]]
    
    def rotateCursorClockwise(self, cursorNo, degrees):
        self.sendMessage("rotate_cursor_clockwise," + str(cursorNo) + "," + str(degrees))

    def rotateCursorAnticlockwise(self, cursorNo, degrees):
        self.sendMessage("rotate_cursor_anticlockwise," + str(cursorNo) + "," + str(degrees))
    
    def getCursorRotation(self, cursorNo):
        rotation = self.sendMessage("get_cursor_rotation," + str(cursorNo))
        return rotation["rotation"]
    
    def moveWindow(self, windowNo, xDistance, yDistance):
        self.sendMessage("move_window," + str(windowNo) + "," + str(xDistance) + "," + str(yDistance))
        
    def relocateWindow(self, windowNo, x, y, surfaceNo):
        self.sendMessage("relocate_window," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(surfaceNo))
        
    def setWindowWidth(self, windowNo, width):
        self.sendMessage("set_window_width," + str(windowNo) + "," + str(width))
        
    def setWindowHeight(self, windowNo, height):
        self.sendMessage("set_window_height," + str(windowNo) + "," + str(height))
        
    def getWindowPosition(self, windowNo):
        loc = self.sendMessage("get_window_pos," + str(windowNo))
        return [loc["x"],loc["y"]]
        
    def getWindowWidth(self, windowNo):
        width = self.sendMessage("get_window_width," + str(windowNo))
        return width["width"]
        
    def getWindowHeight(self, windowNo):
        height = self.sendMessage("get_window_height," + str(windowNo))
        return height["height"]
        
    def stretchWindowDown(self, windowNo, distance):
        self.sendMessage("stretch_window_down," + str(windowNo) + "," + str(distance))
        
    def stretchWindowUp(self, windowNo, distance):
        self.sendMessage("stretch_window_up," + str(windowNo) + "," + str(distance))
        
    def stretchWindowLeft(self, windowNo, distance):
        self.sendMessage("stretch_window_left," + str(windowNo) + "," + str(distance))
        
    def stretchWindowRight(self, windowNo, distance):
        self.sendMessage("stretch_window_right," + str(windowNo) + "," + str(distance))
        
    def setWindowName(self, windowNo, name):
        self.sendMessage("set_window_name," + str(windowNo) + "," + name)
        
    def getWindowName(self, windowNo):
        name = self.sendMessage("get_window_name," + str(windowNo))
        return name["name"]
    
    def relocateCircle(self, elementNo, x, y, windowNo):
        self.elelocs[elementNo] = (x,y)
        self.eletrack[elementNo][0] = True
        
    def getCirclePosition(self, elementNo):
        if (self.elelocs.has_key(elementNo)):
            return [self.elelocs[elementNo][0],self.elelocs[elementNo][1]]
        else:
            loc = self.sendMessage("get_circle_pos," + str(elementNo))
            return [loc["x"],loc["y"]]
    
    def getElementType(self, elementNo):
        type = self.sendMessage("get_element_type," + str(elementNo))
        return type["type"]
    
    def setCircleLineColor(self, elementNo, color):
        self.sendMessage("set_circle_line_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def setCircleFillColor(self, elementNo, color):
        self.sendMessage("set_circle_fill_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))

    def getCircleLineColor(self, elementNo):
        return self.sendMessage("get_circle_line_color," + str(elementNo))
        
    def getCircleFillColor(self, elementNo):
        return self.sendMessage("get_circle_fill_color," + str(elementNo))
    
    def setCircleRadius(self, elementNo, radius):
        self.sendMessage("set_circle_radius," + str(elementNo) + "," + str(radius))
        
    def getCircleRadius(self, elementNo):
        radius = self.sendMessage("get_circle_radius," + str(elementNo))
        return radius["radius"]
    
    def setCircleSides(self, elementNo, sides):
        self.sendMessage("set_circle_sides," + str(elementNo) + "," + str(sides))
        
    def getCircleSides(self, elementNo):
        sides = self.sendMessage("get_circle_sides," + str(elementNo))
        return sides["sides"]
    
    def getLineStart(self, elementNo):
        loc = self.sendMessage("get_line_start," + str(elementNo))
        return [loc["x"],loc["y"]]
    
    def getLineEnd(self, elementNo):
        loc = self.sendMessage("get_line_end," + str(elementNo))
        return [loc["x"],loc["y"]]
    
    def setLineStart(self, elementNo, x, y):
        self.sendMessage("relocate_line_start," + str(elementNo) + "," + str(x) + "," + str(y))
    
    def setLineEnd(self, elementNo, x, y):
        self.sendMessage("relocate_line_end," + str(elementNo) + "," + str(x) + "," + str(y))
    
    def setLineColor(self, elementNo, color):
        self.sendMessage("set_line_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def getLineColor(self, elementNo):
        return self.sendMessage("get_line_color," + str(elementNo))
    
    def setLineWidth(self, elementNo, width):
        self.sendMessage("set_line_width," + str(elementNo) + "," + str(width))
        
    def getLineWidth(self, elementNo):
        width = self.sendMessage("get_line_width," + str(elementNo))
        return width["width"]
    
    def addLineStripPoint(self, elementNo, x, y):
        self.stripLock.acquire()
        self.elelocs[elementNo].append([x,y])
        self.eletrack[elementNo][0] = True
        self.stripLock.release()
        
    def addLineStripPointAt(self, elementNo, x, y, index):
        self.stripLock.acquire()
        self.elelocs[elementNo].insert(index,[x,y])
        self.eletrack[elementNo][0] = True
        self.stripLock.release()
        
    def getLineStripPoint(self, elementNo, pointNo):
        if(self.elelocs.has_key(elementNo)):
            return [self.elelocs[elementNo][pointNo][0],self.elelocs[elementNo][pointNo][0]]
        else:
            loc = self.sendMessage("get_line_strip_point," + str(elementNo) + "," + str(pointNo))
            return [loc["x"],loc["y"]]
    
    def moveLineStripPoint(self, elementNo, pointNo, x, y):
        self.stripLock.acquire()
        self.elelocs[elementNo][pointNo] = [x,y]
        self.eletrack[elementNo][0] = True
        self.stripLock.release()
        
    def getLineStripColor(self, elementNo):
        return self.sendMessage("get_line_strip_color," + str(elementNo))
        
    def setLineStripColor(self, elementNo, color):
        self.sendMessage("set_line_strip_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def setLineStripWidth(self, elementNo, width):
        self.sendMessage("set_line_strip_width," + str(elementNo) + "," + str(width))
        
    def getLineStripWidth(self, elementNo):
        width = self.sendMessage("get_line_strip_width," + str(elementNo))
        return width["width"]
        
    def getLineStripPointCount(self, elementNo):
        count = self.sendMessage("get_line_strip_point_count," + str(elementNo))
        return count["count"]
    
    def setLineStripContent(self, elementNo, content):
        self.stripLock.acquire()
        self.elelock = True
        self.elelocs[elementNo] = [[content[0][0],content[0][1]]]
        for x in range(1,len(content)):
            self.elelocs[elementNo].append([content[x][0],content[x][1]])
        self.eletrack[elementNo][0] = True
        self.stripLock.release()
    
    def addPolygonPoint(self, elementNo, x, y):
        self.sendMessage("add_polygon_point," + str(elementNo) + "," + str(x) + "," + str(y))
        
    def getPolygonPoint(self, elementNo, pointNo):
        loc = self.sendMessage("get_polygon_point," + str(elementNo) + "," + str(pointNo))
        return (loc["x"],loc["y"])
    
    def movePolygonPoint(self, elementNo, pointNo, x, y):
        self.sendMessage("relocate_polygon_point," + str(elementNo) + "," + str(pointNo) + "," + str(x) + "," + str(y))
        
    def getPolygonFillColor(self, elementNo):
        return self.sendMessage("get_polygon_fill_color," + str(elementNo))
    
    def setPolygonFillColor(self, elementNo, color):
        self.sendMessage("set_polygon_fill_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def getPolygonLineColor(self, elementNo):
        return self.sendMessage("get_polygon_line_color," + str(elementNo))
    
    def setPolygonLineColor(self, elementNo, color):
        self.sendMessage("set_polygon_line_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def getPolygonPointCount(self, elementNo):
        count = self.sendMessage("get_polygon_point_count," + str(elementNo))
        return count["count"]
    
    def setRectangleTopLeft(self, elementNo, x, y):
        self.sendMessage("set_rectangle_top_left," + str(elementNo) + "," + str(x) + "," + str(y))
        
    def getRectangleTopLeft(self, elementNo):
        pos = self.sendMessage("get_rectangle_top_left," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleTopRight(self, elementNo):
        pos = self.sendMessage("get_rectangle_top_right," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleBottomRight(self, elementNo):
        pos = self.sendMessage("get_rectangle_bottom_right," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleBottomLeft(self, elementNo):
        pos = self.sendMessage("get_rectangle_bottom_left," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def setRectangleWidth(self, elementNo, width):
        self.sendMessage("set_rectangle_width," + str(elementNo) + "," + str(width))
        
    def getRectangleWidth(self, elementNo):
        width = self.sendMessage("get_rectangle_width," + str(elementNo))
        return float(width["width"])
        
    def setRectangleHeight(self, elementNo, height):
        self.sendMessage("set_rectangle_height," + str(elementNo) + "," + str(height))
        
    def getRectangleHeight(self, elementNo):
        height = self.sendMessage("get_rectangle_height," + str(elementNo))
        return float(height["height"])
    
    def setRectangleFillColor(self, elementNo, color):
        self.sendMessage("set_rectangle_fill_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def getRectangleFillColor(self, elementNo):
        return self.sendMessage("get_rectangle_fill_color," + str(elementNo))
    
    def setRectangleLineColor(self, elementNo, color):
        self.sendMessage("set_rectangle_line_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def getRectangleLineColor(self, elementNo):
        return self.sendMessage("get_rectangle_line_color," + str(elementNo))
    
    def setTexRectangleTopLeft(self, elementNo, x, y):
        self.sendMessage("set_texrectangle_top_left," + str(elementNo) + "," + str(x) + "," + str(y))
        
    def getTexRectangleTopLeft(self, elementNo):
        pos = self.sendMessage("get_texrectangle_top_left," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleTopRight(self, elementNo):
        pos = self.sendMessage("get_texrectangle_top_right," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleBottomRight(self, elementNo):
        pos = self.sendMessage("get_texrectangle_bottom_right," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleBottomLeft(self, elementNo):
        pos = self.sendMessage("get_texrectangle_bottom_left," + str(elementNo))
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleTexture(self, elementNo):
        tex = self.sendMessage("get_texrectangle_texture," + str(elementNo))
        return tex["texture"]
    
    def setTexRectangleTexture(self, elementNo, texture):
        self.sendMessage("set_texrectangle_texture," + str(elementNo) + "," + str(texture))
    
    def setTexRectangleWidth(self, elementNo, width):
        self.sendMessage("set_texrectangle_width," + str(elementNo) + "," + str(width))
        
    def getTexRectangleWidth(self, elementNo):
        width = self.sendMessage("get_texrectangle_width," + str(elementNo))
        return float(width["width"])
        
    def setTexRectangleHeight(self, elementNo, height):
        self.sendMessage("set_texrectangle_height," + str(elementNo) + "," + str(height))
        
    def getTexRectangleHeight(self, elementNo):
        height = self.sendMessage("get_texrectangle_height," + str(elementNo))
        return float(height["height"])
    
    def setText(self, elementNo, text):
        self.sendMessage("set_text," + str(elementNo) + "," + text)
        
    def getText(self, elementNo):
        text = self.sendMessage("get_text," + str(elementNo))
        return text["text"]
    
    def setTextPosition(self, elementNo, x, y, windowNo):
        self.sendMessage("relocate_text," + str(elementNo) + "," + str(x) + "," + str(y) + "," + str(windowNo))
        
    def getTextPosition(self, elementNo):
        loc = self.sendMessage("get_text_pos," + str(elementNo))
        return [loc["x"],loc["y"]]
        
    def setPointSize(self, elementNo, pointSize):
        self.sendMessage("set_text_point_size," + str(elementNo) + "," + str(pointSize))
        
    def getPointSize(self, elementNo):
        size = self.sendMessage("get_text_point_size," + str(elementNo))
        return size["size"]
    
    def getFont(self, elementNo):
        font = self.sendMessage("get_text_font," + str(elementNo))
        return font["font"]
    
    def setFont(self, elementNo, font):
        self.sendMessage("set_text_font," + str(elementNo) + "," + font)
        
    def setTextColor(self, elementNo, color):
        self.sendMessage("set_text_color," + str(elementNo) + "," + self.colorString(color[0], color[1], color[2], color[3]))
        
    def showElement(self, elementNo):
        self.sendMessaqe("show_element," + str(elementNo))
        
    def hideElement(self, elementNo):
        self.sendMessage("hide_element," + str(elementNo))
        
    def checkElementVisibility(self, elementNo):
        visibility = self.sendMessage("check_element_visibility," + str(elementNo))
        return visibility["visible"]
        
    def hideSetupSurface(self):
        self.sendMessage("hide_setup_surface")
        
    def showSetupSurface(self):
        self.sendMessage("show_setup_surface")
        
    def getSetupSurfaceVisibility(self):
        return self.sendMessage("get_setup_surface_visibility")
        
    def getClickedElements(self, surfaceNo, x, y):
        elements = self.sendMessage("get_clicked_elements," + str(surfaceNo) + "," + str(x) + "," + str(y))
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist