import socket, sys, select

class messageSender:
    __slots__ = ['s']
    HOST = 'localhost'
    PORT = 5000
    ERRORS = {1 : "Invalid API call",
              2 : "Wrong number of arguments (% instead of %)",
              3 : "User name not yet set",
              4 : "User name already set",
              5 : "Application name already set",
              6 : "Application name not yet set",
              7 : "Must be owner to change admin setting"
    }
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(2)
        
        try:
            self.s.connect((self.HOST,self.PORT))
        except:
            print 'Unable to connect'
            sys.exit()
            
        print 'Connected to remote host. Start sending messages'
        
    def sendMessage(self, message):
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
                    return dict
                except:
                    return dict
                
    def quit(self):
        self.sendMessage("quit")
        
    def login(self, username):
        self.sendMessage("login," + str(username))
        
    def setapp(self, appname):
        self.sendMessage("setapp," + str(appname))
    
    def newSurface(self):
        self.sendMessage("new_surface")
        
    def newSurfaceWithID(self, ID):
        self.sendMessage("new_surface_with_ID," + str(ID))
    
    def newCursor(self, surfaceNo, x, y):
        return self.sendMessage("new_cursor," + str(surfaceNo) + "," + str(x) + "," + str(y))
    
    def newCursorWithID(self, ID, surfaceNo, x, y):
        return self.sendMessage("new_cursor_with_ID," + str(ID) + "," + str(surfaceNo) + "," + str(x) + "," + str(y))
    
    def newWindow(self, surfaceNo, x, y, width, height, name):
        return self.sendMessage("new_window," + str(surfaceNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + name)
    
    def newWindowWithID(self, ID, surfaceNo, x, y, width, height, name):
        return self.sendMessage("new_window_with_ID," + str(ID) + "," + str(surfaceNo) + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + name)
    
    def newCircle(self, windowNo, x, y, radius, lineCol, fillCol):
        return self.sendMessage("new_circle," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(radius) + "," + lineCol + "," + fillCol)
    
    def newCircleWithID(self, ID, windowNo, x, y, radius, lineCol, fillCol):
        return self.sendMessage("new_circle_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(radius) + "," + lineCol + "," + fillCol)
    
    def newLine(self, windowNo, xStart, yStart, xEnd, yEnd, Color):
        return self.sendMessage("new_line," + str(windowNo) + "," + str(xStart) + "," + str(yStart) + "," + str(xEnd) + "," + str(yEnd) + "," + Color)
    
    def newLineWithID(self, ID, windowNo, xStart, yStart, xEnd, yEnd, Color):
        return self.sendMessage("new_line_with_ID," + str(ID) + "," + str(windowNo) + "," + str(xStart) + "," + str(yStart) + "," + str(xEnd) + "," + str(yEnd) + "," + Color)
    
    def newLineStrip(self, windowNo, x, y, Color):
        return self.sendMessage("new_line_strip," + str(windowNo) + "," + str(x) + "," + str(y) + "," + Color)
    
    def newLineStripWithID(self, ID, windowNo, x, y, Color):
        return self.sendMessage("new_line_strip_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + Color)
    
    def newPolygon(self, windowNo, x, y, lineColor, fillColor):
        return self.sendMessage("new_polygon," + str(windowNo) + "," + str(x) + "," + str(y) + "," + lineColor + "," + fillColor)
    
    def newPolygonWithID(self, ID, windowNo, x, y, lineColor, fillColor):
        return self.sendMessage("new_polygon_with_ID," + str(ID) + "," + str(windowNo) + "," + str(x) + "," + str(y) + "," + lineColor + "," + fillColor)
    
    def newText(self, windowNo, text, x, y, ptSize, font, color):
        return self.sendMessage("new_text," + str(windowNo) + "," + text + "," + str(x) + "," + str(y) + "," + str(ptSize) + "," + font + "," + color)
    
    def newTextWithID(self, ID, windowNo, text, x, y, ptSize, font, color):
        return self.sendMessage("new_text_with_ID," + str(ID) + "," + str(windowNo) + "," + text + "," + str(x) + "," + str(y) + "," + str(ptSize) + "," + font + "," + color)
    
    def subscribeToSurface(self, surfaceNo):
        self.sendMessage("subscribe_to_surface," + str(surfaceNo))
    
    def getSurfaceID(self, surfaceNo):
        return self.sendMessage("get_surface_ID," + str(surfaceNo))
    
    def setSurfaceID(self, surfaceNo, ID):
        self.sendMessage("set_surface_ID," + str(surfaceNo) + "," + str(ID))
    
    def getSurfaceOwner(self, surfaceNo):
        self.sendMessage("get_surface_owner," + str(surfaceNo))
        
    def getSurfaceAppDetails(self, surfaceNo):
        self.sendMessage("get_surface_app_details," + str(surfaceNo))
        
    def getSurfacesByID(self, ID):
        return self.sendMessage("get_surfaces_by_ID," + str(ID))
        
    def getSurfacesByOwner(self, owner):
        return self.sendMessage("get_surfaces_by_owner," + str(owner))
        
    def getSurfacesByAppName(self, name):
        return self.sendMessage("get_surfaces_by_app_name," +  str(name))
        
    def getSurfacesByAppDetails(self, name, instance):
        return self.sendMessage("get_surfaces_by_app_details" + str(name) + "," + str(instance))
        
    def becomeSurfaceAdmin(self, surfaceNo):
        self.sendMessage("become_surface_admin," + str(surfaceNo))
        
    def stopBeingSurfaceAdmin(self, surfaceNo):
        self.sendMessage("stop_being_surface_admin," + str(surfaceNo))
        
    def subscribeToWindow(self, windowNo):
        self.sendMessage("subscribe_to_window," + str(windowNo))
        
    def getWindowID(self, windowNo):
        return self.sendMessage("get_window_ID," + str(windowNo))
    
    def setWindowID(self, windowNo, ID):
        self.sendMessage("set_window_ID," + str(windowNo) + "," + str(ID))
    
    def getWindowOwner(self, windowNo):
        self.sendMessage("get_window_owner," + str(windowNo))
        
    def getWindowAppDetails(self, surfaceNo):
        self.sendMessage("get_window_app_details," + str(surfaceNo))
        
    def getWindowsByID(self, ID):
        return self.sendMessage("get_windows_by_ID," + str(ID))
        
    def getWindowsByOwner(self, owner):
        return self.sendMessage("get_windows_by_owner," + str(owner))
        
    def getWindowsByAppName(self, name):
        return self.sendMessage("get_windows_by_app_name," +  str(name))
        
    def getWindowssByAppDetails(self, name, instance):
        return self.sendMessage("get_windows_by_app_details" + str(name) + "," + str(instance))
        
    def becomeWindowAdmin(self, windowNo):
        self.sendMessage("become_window_admin," + str(windowNo))
        
    def stopBeingWindowAdmin(self, windowNo):
        self.sendMessage("stop_being_window_admin," + str(windowNo))
        
    def subscribeToElement(self, elementNo):
        self.sendMessage("subscribe_to_element," + str(elementNo))
        
    def getElementID(self, elementNo):
        return self.sendMessage("get_element_ID," + str(elementNo))
    
    def setElementID(self, elementNo, ID):
        self.sendMessage("set_element_ID," + str(elementNo) + "," + str(ID))
    
    def getElementOwner(self, elementNo):
        self.sendMessage("get_element_owner," + str(elementNo))
        
    def getElementAppDetails(self, surfaceNo):
        self.sendMessage("get_element_app_details," + str(surfaceNo))
        
    def getElementsByID(self, ID):
        return self.sendMessage("get_elements_by_ID," + str(ID))
        
    def getElementsByOwner(self, owner):
        return self.sendMessage("get_elements_by_owner," + str(owner))
        
    def getElementsByAppName(self, name):
        return self.sendMessage("get_elements_by_app_name," +  str(name))
        
    def getElementsByAppDetails(self, name, instance):
        return self.sendMessage("get_elements_by_app_details" + str(name) + "," + str(instance))
        
    def becomeElementAdmin(self, elementNo):
        self.sendMessage("become_element_admin," + str(elementNo))
        
    def stopBeingElementAdmin(self, elementNo):
        self.sendMessage("stop_being_element_admin," + str(elementNo))
    
    def mouseLeftDown(self, cursorNo):
        return self.sendMessage("mouse_l," + str(cursorNo))
    
    def mouseLeftUp(self, cursorNo):
        return self.sendMessage("mouse_lu," + str(cursorNo))
    
    def mouseMiddleDown(self, cursorNo):
        return self.sendMessage("mouse_m," + str(cursorNo))
    
    def mouseMiddleUp(self, cursorNo):
        return self.sendMessage("mouse_mu," + str(cursorNo))
    
    def mouseRightDown(self, cursorNo):
        return self.sendMessage("mouse_r," + str(cursorNo))
    
    def mouseRightUp(self, cursorNo):
        return self.sendMessage("mouse_ru," + str(cursorNo))
    
    def moveCursor(self, cursorNo, xDistance, yDistance):
        self.sendMessage("move_cursor," + str(cursorNo) + "," + str(xDistance) + "," + str(yDistance))
        
    def testMoveCursor(self, cursorNo, xDistance, yDistance):
        return self.sendMessage("test_move_cursor," + str(cursorNo) + "," + str(xDistance) + "," + str(yDistance))
    
    def relocateCursor(self, cursorNo, x, y, surfaceNo):
        self.sendMessage("relocate_cursor," + str(cursorNo) + "," + str(x) + "," + str(y) + "," + str(surfaceNo))
    
    def getCursorPosition(self, cursorNo):
        return self.sendMessage("get_cursor_pos," + str(cursorNo))
    
    def rotateCursorClockwise(self, cursorNo, degrees):
        self.sendMessage("rotate_cursor_clockwise," + str(cursorNo) + "," + str(degrees))

    def rotateCursorAnticlockwise(self, cursorNo, degrees):
        self.sendMessage("rotate_cursor_anticlockwise," + str(cursorNo) + "," + str(degrees))
    
    def getCursorRotation(self, cursorNo):
        return self.sendMessage("get_cursor_rotation," + str(cursorNo))
    
    def moveWindow(self, windowNo, xDistance, yDistance):
        self.sendMessage("move_window," + str(windowNo) + "," + str(xDistance) + "," + str(yDistance))
        
    def relocateWindow(self, windowNo, x, y, surfaceNo):
        self.sendMessage("relocate_window," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(surfaceNo))
        
    def setWindowWidth(self, windowNo, width):
        self.sendMessage("set_window_width," + str(windowNo) + "," + str(width))
        
    def setWindowHeight(self, windowNo, height):
        self.sendMessage("set_window_height," + str(windowNo) + "," + str(height))
        
    def getWindowPosition(self, windowNo):
        return self.sendMessage("get_window_pos," + str(windowNo))
        
    def getWindowWidth(self, windowNo):
        return self.sendMessage("get_window_width," + str(windowNo))
        
    def getWindowHeight(self, windowNo):
        return self.sendMessage("get_window_height," + str(windowNo))
        
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
        return self.sendMessage("get_window_name," + str(windowNo))
    
    def relocateCircle(self, elementNo, x, y, windowNo):
        self.sendMessage("relocate_circle," + str(elementNo) + "," + str(x) + "," + str(y) + "," + str(windowNo))
        
    def getCirclePosition(self, elementNo):
        return self.sendMessage("get_circle_pos," + str(elementNo))
    
    def getElementType(self, elementNo):
        return self.sendMessage("get_element_type," + str(elementNo))
    
    def setCircleLineColor(self, elementNo, color):
        self.sendMessage("set_circle_line_color," + str(elementNo) + "," + color)
        
    def setCircleFillColor(self, elementNo, color):
        self.sendMessage("set_circle_fill_color," + str(elementNo) + "," + color)

    def getCircleLineColor(self, elementNo):
        return self.sendMessage("get_circle_line_color," + str(elementNo))
        
    def getCircleFillColor(self, elementNo):
        return self.sendMessage("get_circle_fill_color," + str(elementNo))
    
    def setCircleRadius(self, elementNo, radius):
        self.sendMessage("set_circle_radius," + str(elementNo) + "," + str(radius))
        
    def getCircleRadius(self, elementNo):
        return self.sendMessage("get_circle_radius," + str(elementNo))
    
    def getLineStart(self, elementNo):
        return self.sendMessage("get_line_start," + str(elementNo))
    
    def getLineEnd(self, elementNo):
        return self.sendMessage("get_line_end," + str(elementNo))
    
    def setLineStart(self, elementNo, x, y):
        self.sendMessage("relocate_line_start," + str(elementNo) + "," + str(x) + "," + str(y))
    
    def setLineEnd(self, elementNo, x, y):
        self.sendMessage("relocate_line_end," + str(elementNo) + "," + str(x) + "," + str(y))
    
    def setLineColor(self, elementNo, x, y):
        self.sendMessage("set_line_color," + str(elementNo) + "," + str(x) + "," + str(y))
        
    def getLineColor(self, elementNo):
        return self.sendMessage("get_line_color," + str(elementNo))
    
    def addLineStripPoint(self, elementNo, x, y):
        self.sendMessage("add_line_strip_point," + str(elementNo) + "," + str(x) + "," + str(y))
        
    def addLineStripPointAt(self, elementNo, x, y, index):
        self.sendMessage("add_line_strip_point_at," + str(elementNo) + "," + str(x) + "," + str(y) + "," + str(index))
        
    def getLineStripPoint(self, elementNo, pointNo):
        return self.sendMessage("get_line_strip_point," + str(elementNo) + "," + str(pointNo))
    
    def moveLineStripPoint(self, elementNo, pointNo, x, y):
        self.sendMessage("relocate_line_strip_point," + str(elementNo) + "," + str(pointNo) + "," + str(x) + "," + str(y))
        
    def getLineStripColor(self, elementNo):
        return self.sendMessage("get_line_strip_color," + str(elementNo))
        
    def setLineStripColor(self, elementNo, color):
        self.sendMessage("set_line_strip_color," + str(elementNo) + "," + color)
        
    def getLineStripPointCount(self, elementNo):
        return self.sendMessage("get_line_strip_point_count," + str(elementNo))
    
    def addPolygonPoint(self, elementNo, x, y):
        self.sendMessage("add_polygon_point," + str(elementNo) + "," + str(x) + "," + str(y))
        
    def getPolygonPoint(self, elementNo, pointNo):
        return self.sendMessage("get_polygon_point," + str(elementNo) + "," + str(pointNo))
    
    def movePolygonPoint(self, elementNo, pointNo, x, y):
        self.sendMessage("relocate_polygon_point," + str(elementNo) + "," + str(pointNo) + "," + str(x) + "," + str(y))
        
    def getPolygonFillColor(self, elementNo):
        return self.sendMessage("get_polygon_fill_color," + str(elementNo))
    
    def setPolygonFillColor(self, elementNo, color):
        self.sendMessage("set_polygon_fill_color," + str(elementNo) + "," + color)
        
    def getPolygonLineColor(self, elementNo):
        return self.sendMessage("get_polygon_line_color," + str(elementNo))
    
    def setPolygonLineColor(self, elementNo, color):
        self.sendMessage("set_polygon_line_color," + str(elementNo) + "," + color)
        
    def getPolygonPointCount(self, elementNo):
        return self.sendMessage("get_polygon_point_count," + str(elementNo))
    
    def setText(self, elementNo, text):
        self.sendMessage("set_text," + str(elementNo) + "," + text)
        
    def getText(self, elementNo):
        return self.sendMessage("get_text," + str(elementNo))
    
    def setTextPosition(self, elementNo, x, y, windowNo):
        self.sendMessage("relocate_text," + str(elementNo) + "," + str(x) + "," + str(y) + "," + str(windowNo))
        
    def getTextPosition(self, elementNo):
        return self.sendMessage("get_text_pos," + str(elementNo))
        
    def setPointSize(self, elementNo, pointSize):
        self.sendMessage("set_text_point_size," + str(elementNo) + "," + str(pointSize))
        
    def getPointSize(self, elementNo):
        return self.sendMessage("get_text_point_size," + str(elementNo))
    
    def getFont(self, elementNo):
        return self.sendMessage("get_text_font," + str(elementNo))
    
    def setFont(self, elementNo, font):
        self.sendMessage("set_text_font," + str(elementNo) + "," + font)
        
    def setTextColor(self, elementNo, color):
        self.sendMessage("set_text_color," + str(elementNo) + "," + color)
        
    def showElement(self, elementNo):
        self.sendMessaqe("show_element," + str(elementNo))
        
    def hideElement(self, elementNo):
        self.sendMessage("hide_element," + str(elementNo))
        
    def checkElementVisibility(self, elementNo):
        self.sendMessage("check_element_visibility," + str(elementNo))
        
    def hideSetupSurface(self):
        self.sendMessage("hide_setup_surface")
        
    def showSetupSurface(self):
        self.sendMessage("show_setup_surface")
        
    def getSetupSurfaceVisibility(self):
        return self.sendMessage("get_setup_surface_visibility")
        
    def getClickedElements(self, surfaceNo, x, y):
        return self.sendMessage("get_clicked_elements," + str(surfaceNo) + "," + str(x) + "," + str(y))