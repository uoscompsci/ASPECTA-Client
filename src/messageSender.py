import socket, sys, select

class messageSender:
    __slots__ = ['s']
    HOST = 'localhost'
    PORT = 5000
    ERRORS = {1 : "Invalid API call",
              2 : "Wrong number of arguments (% instead of %)"
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
    
    def newSurface(self):
        self.sendMessage("new_surface")
    
    def newCursor(self, surfaceNo, x, y):
        return self.sendMessage("new_cursor," + str(surfaceNo) + "," + str(x) + "," + str(y))
    
    def newWindow(self, surfaceNo, x, y, width, height, name):
        return self.sendMessage("new_window," + str(surfaceNo), + "," + str(x) + "," + str(y) + "," + str(width) + "," + str(height) + "," + name)
    
    def newCircle(self, windowNo, x, y, radius, lineCol, fillCol):
        return self.sendMessage("new_circle," + str(windowNo) + "," + str(x) + "," + str(y) + "," + str(radius) + "," + lineCol + "," + fillCol)
    
    def newLine(self, windowNo, xStart, yStart, xEnd, yEnd, Color):
        return self.sendMessage("new_line," + str(windowNo) + "," + str(xStart) + "," + str(yStart) + "," + str(xEnd) + "," + str(yEnd) + "," + Color)
    
    def newLineStrip(self, windowNo, x, y, Color):
        return self.sendMessage("new_line_strip," + str(windowNo) + "," + str(x) + "," + str(y) + "," + Color)
    
    def newPolygon(self, windowNo, x, y, lineColor, fillColor):
        return self.sendMessage("new_polygon," + str(windowNo) + "," + str(x) + "," + str(y) + "," + lineColor + "," + fillColor)
    
    def newText(self, windowNo, text, x, y, ptSize, font, color):
        return self.sendMessage("new_text," + str(windowNo) + "," + text + "," + str(x) + "," + str(y) + "," + str(ptSize) + "," + font + "," + color)
    
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
        
    def getWindowPos(self, windowNo):
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