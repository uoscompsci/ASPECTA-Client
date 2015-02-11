import socket, sys, select, time, threading
import ujson as json
from ConfigParser import SafeConfigParser
import base64

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
    loop = True
    
    def encode_length(self, l):
        l = str(l)
        while len(l) < 8:
            l = "0" + l
        return l

    def uploadImage(self, file):
        filename = file.split("/")
        filename = filename[-1]
        self.sendMessage({'call' : 'set_upload_name', 'filename' : filename})
        time.sleep(0.5)
        s = socket.socket()
        s.connect((self.host,self.port+1))
        imageNo = s.recv(1024)
        
        f=open(file, "rb") 
        data=f.read()
        
        s.sendall(self.encode_length(len(data)))
        s.sendall(data)
        
        l = f.read(1024)
        while (l):
            s.send(l)
            l = f.read(1024)
        f.close()
        
        s.recv(1)
        s.close()
        return int(imageNo)
    
    def eleUpdater(self):
        while self.loop:
            #print str(self.eletrack)
            strips = 0
            for x in range(0,len(self.elelocs)):
                try:
                    if(self.eletrack[self.elelocs.keys()[x]][0] == True):
                        if(self.eletrack[self.elelocs.keys()[x]][1] == "lineStrip"):
                            strips += 1
                            self.stripLock.acquire()
                            converted = str(self.elelocs[self.elelocs.keys()[x]][0][0]) + ":" + str(self.elelocs[self.elelocs.keys()[x]][0][1])
                            for y in range(0,len(self.elelocs[self.elelocs.keys()[x]])):
                                converted += ";" + str(self.elelocs[self.elelocs.keys()[x]][y][0]) + ":" + str(self.elelocs[self.elelocs.keys()[x]][y][1])
                            self.sendMessage({'call' : 'set_line_strip_content', 
                                              'elementNo' : str(self.elelocs.keys()[x]), 
                                              'content' : converted})
                            self.stripLock.release()
                        elif(self.eletrack[self.elelocs.keys()[x]][1] == "circle"):
                            self.sendMessage({'call' : 'relocate_circle', 
                                              'elementNo' : str(self.elelocs.keys()[x]), 
                                              'x' : str(self.elelocs[self.elelocs.keys()[x]][0]), 
                                              'y' : str(self.elelocs[self.elelocs.keys()[x]][1])})
                        self.eletrack[self.elelocs.keys()[x]][0]=False
                except IndexError, e:
                    pass
            time.sleep(self.refreshrate)
        print "Closing"
    
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        self.refreshrate = 1/(parser.getint('library','MovesPerSecond'))
        self.host = parser.get('connection','host')
        self.port = parser.getint('connection','port')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
    
    def colorTuple(self, string):
        colortuple = string.split(":")
        for x in range(0,4):
            colortuple[x] = float(colortuple[x])
        return colortuple
        
    def sendMessage(self, message):
        self.sendlock.acquire()
        self.sending+=1
        #print "Sending " + str(self.sending)
        jsonmessage = json.dumps(message)
        lengthorig = str(len(jsonmessage))
        toadd = 10-len(lengthorig)
        genstring = ""
        while (toadd>0):
            genstring+="0"
            toadd-=1
        length = genstring + lengthorig
        self.s.send(length)
        n = 1024
        splitjson = [jsonmessage[i:i+n] for i in range(0, len(jsonmessage), n)]
        for x in range(0, len(splitjson)):
            self.s.send(splitjson[x])
        if(message=="quit"):
            print '\033[1;31mShutting down client\033[1;m'
            self.loop=False
        socket_list = [sys.stdin, self.s]
        read_sockets = select.select(socket_list , [], [])[0]
        
        for sock in read_sockets:
            data = json.loads(sock.recv(4096))
            try:
                errno = data["error"]
                error = str(self.ERRORS[errno])
                spliterr = error.split("%")
                errorStr = spliterr[0]
                for x in range(1,len(spliterr)):
                    errorStr = errorStr + data[str(x)] + spliterr[x]
                print "\033[1;31mERROR: " + errorStr + "\033[1;m"
                self.sendlock.release()
                return data
            except:
                self.sendlock.release()
                return data
                
    def quit(self):
        self.sendMessage({'call' : 'quit'})
        self.loop=False
        self.eletrack = {}
        self.elelocs = {}
        
    def quitClientOnly(self):
        self.loop=False
        self.eletrack = {}
        self.elelocs = {}
        
    def login(self, username):
        self.sendMessage({'call' : 'login', 
                          'username' : str(username)})
        
    def setapp(self, appname):
        self.sendMessage({'call' : 'setapp', 
                          'appname' : str(appname)})
    
    def newSurface(self):
        sur = self.sendMessage({'call' : 'new_surface'})
        surNo = int(sur["surfaceNo"])
        return surNo
        
    def newSurfaceWithID(self, ID):
        return self.sendMessage({'call' : 'new_surface_with_ID', 
                                 'ID' : str(ID)})
    
    def newCursor(self, surfaceNo, x, y):
        cur = self.sendMessage({'call' : 'new_cursor', 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' : str(y)})
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newCursorWithID(self, ID, surfaceNo, x, y):
        cur = self.sendMessage({'call' : 'new_cursor_with_ID', 
                                'ID' : str(ID), 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' : str(y)})
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newWindow(self, surfaceNo, x, y, width, height, name):
        win = self.sendMessage({'call' : 'new_window', 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' :  str(y), 
                                'width' : str(width), 
                                'height' : str(height), 
                                'name' : name})
        winNo = int(win["windowNo"])
        return winNo
    
    def newWindowWithID(self, ID, surfaceNo, x, y, width, height, name):
        win = self.sendMessage({'call' : 'new_window_with_ID', 
                                'ID' : str(ID), 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' :  str(y), 
                                'width' : str(width), 
                                'height' : str(height), 
                                'name' : name})
        winNo = int(win["windowNo"])
        return winNo
    
    def newCircle(self, windowNo, x, y, radius, lineCol, lineWidth, fillCol, sides):
        ele = self.sendMessage({'call' : 'new_circle', 
                                'windowNo' :  str(windowNo), 
                                'x' : str(x), 
                                'y' : str(y), 
                                'radius' : str(radius), 
                                'lineColor' : self.colorString(lineCol[0], lineCol[1], lineCol[2], lineCol[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillCol[0], fillCol[1], fillCol[2], fillCol[3]), 
                                'sides' : str(sides)})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"circle"]
        return eleNo
    
    def newCircleWithID(self, ID, windowNo, x, y, radius, lineCol, lineWidth, fillCol, sides):
        ele = self.sendMessage({'call' : 'new_circle_with_ID',
                                'ID' : str(ID),
                                'windowNo' : str(windowNo),
                                'x' : str(x),
                                'y' : str(y),
                                'radius' : str(radius), 
                                'lineColor' : self.colorString(lineCol[0], lineCol[1], lineCol[2], lineCol[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillCol[0], fillCol[1], fillCol[2], fillCol[3]),
                                'sides' : str(sides)})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"circle"]
        return eleNo
    
    def newLine(self, windowNo, xStart, yStart, xEnd, yEnd, color, width):
        ele = self.sendMessage({'call' : 'new_line',
                                'windowNo' : str(windowNo),
                                'xStart' : str(xStart),
                                'yStart' : str(yStart),
                                'xEnd' : str(xEnd),
                                'yEnd' : str(yEnd),
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (xStart,yStart,xEnd,yEnd)
        self.eletrack[eleNo] = [True,"line"]
        return eleNo
    
    def newLineWithID(self, ID, windowNo, xStart, yStart, xEnd, yEnd, color, width):
        ele = self.sendMessage({'call' : 'new_line_with_ID',
                                'ID' : str(ID),
                                'windowNo' : str(windowNo),
                                'xStart' : str(xStart),
                                'yStart' : str(yStart),
                                'xEnd' : str(xEnd),
                                'yEnd' : str(yEnd),
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (xStart,yStart,xEnd,yEnd)
        self.eletrack[eleNo] = [True,"line"]
        return eleNo
    
    def newLineStrip(self, windowNo, x, y, color, width):
        ele = self.sendMessage({'call' : 'new_line_strip', 
                                'windowNo' : str(windowNo),
                                'x' : str(x),
                                'y' : str(y),
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"lineStrip"]
        return eleNo
    
    def newLineStripWithID(self, ID, windowNo, x, y, color, width):
        ele = self.sendMessage({'call' : 'new_line_strip_with_ID',
                                'ID' : str(ID), 
                                'windowNo' : str(windowNo),
                                'x' : str(x),
                                'y' : str(y),
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"lineStrip"]
        return eleNo
    
    def newPolygon(self, windowNo, x, y, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_polygon',
                                'windowNo' : str(windowNo),
                                'x' : str(x),
                                'y' : str(y),
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"polygon"]
        return eleNo
    
    def newPolygonWithID(self, ID, windowNo, x, y, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_polygon_with_ID',
                                'ID' : str(ID),
                                'windowNo' : str(windowNo),
                                'x' : str(x),
                                'y' : str(y),
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = [[x,y]]
        self.eletrack[eleNo] = [True,"polygon"]
        return eleNo
    
    def newTexRectangle(self, windowNo, x, y, width, height, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ele = self.sendMessage({'call' : 'new_texrectangle',
                                    'windowNo' : str(windowNo),
                                    'x' : str(x),
                                    'y' : str(y),
                                    'width' : str(width),
                                    'height' : str(height),
                                    'textureData' : encoded_string,
                                    'extension' : extension})
            eleNo = int(ele["elementNo"])
            self.elelocs[eleNo] = (x,y)
            self.eletrack[eleNo] = [True,"texrectangle"]
            return eleNo
    
    def newTexRectangleWithID(self, ID, windowNo, x, y, width, height, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ele = self.sendMessage({'call' : 'new_texrectangle_with_ID',
                                    'ID' : str(ID),
                                    'windowNo' : str(windowNo),
                                    'x' : str(x),
                                    'y' : str(y),
                                    'width' : str(width),
                                    'height' : str(height),
                                    'textureData' : encoded_string,
                                    'extension' : extension})
            eleNo = int(ele["elementNo"])
            self.elelocs[eleNo] = (x,y)
            self.eletrack[eleNo] = [True,"texrectangle"]
            return eleNo
    
    def newRectangle(self, windowNo, x, y, width, height, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_rectangle',
                                'windowNo' : str(windowNo), 
                                'x' : str(x),
                                'y' : str(y),
                                'width' : str(width),
                                'height' : str(height),
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"rectangle"]
        return eleNo
    
    def newRectangleWithID(self, ID, windowNo, x, y, width, height, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_rectangle_with_ID',
                                'ID' : str(ID),
                                'windowNo' : str(windowNo), 
                                'x' : str(x),
                                'y' : str(y),
                                'width' : str(width),
                                'height' : str(height),
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"rectangle"]
        return eleNo
    
    def newText(self, windowNo, text, x, y, ptSize, font, color):
        ele = self.sendMessage({'call' : 'new_text',
                                'windowNo' : str(windowNo),
                                'text' : text,
                                'x' : str(x),
                                'y' : str(y),
                                'ptSize' : str(ptSize),
                                'font' : font,
                                'color' : self.colorString(color[0], color[1], color[2], color[3])})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"text"]
        return eleNo
    
    def newTextWithID(self, ID, windowNo, text, x, y, ptSize, font, color):
        ele = self.sendMessage({'call' : 'new_text_with_ID',
                                'ID' : str(ID),
                                'windowNo' : str(windowNo),
                                'text' : text,
                                'x' : str(x),
                                'y' : str(y),
                                'pt' : str(ptSize),
                                'font' : font,
                                'color' : self.colorString(color[0], color[1], color[2], color[3])})
        eleNo = int(ele["elementNo"])
        self.elelocs[eleNo] = (x,y)
        self.eletrack[eleNo] = [True,"text"]
        return eleNo
    
    def subscribeToSurface(self, surfaceNo):
        self.sendMessage({'call' : 'subscribe_to_surface',
                          'surfaceNo' : str(surfaceNo)})
    
    def getSurfaceID(self, surfaceNo):
        ID = self.sendMessage({'call' : 'get_surface_ID',
                               'surfaceNo' : str(surfaceNo)})
        return ID["ID"]
    
    def setSurfaceID(self, surfaceNo, ID):
        self.sendMessage({'call' : 'set_surface_ID',
                          'surfaceNo' : str(surfaceNo),
                          'ID' : str(ID)})
    
    def getSurfaceOwner(self, surfaceNo):
        owner = self.sendMessage({'call' : 'get_surface_owner',
                                  'surfaceNo' : str(surfaceNo)})
        return owner["owner"]
        
    def getSurfaceAppDetails(self, surfaceNo):
        details = self.sendMessage({'call' : 'get_surface_app_details',
                                    'surfaceNo' : str(surfaceNo)})
        return (details["app"],details["instance"])
        
    def getSurfacesByID(self, ID):
        surfaces = self.sendMessage({'call' : 'get_surfaces_by_ID',
                                    'ID' : str(ID)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByOwner(self, owner):
        surfaces = self.sendMessage({'call' : 'get_surfaces_by_owner',
                                     'owner' : str(owner)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByAppName(self, name):
        surfaces = self.sendMessage({'call' : 'get_surfaces_by_app_name',
                                     'name' : str(name)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByAppDetails(self, name, instance):
        surfaces = self.sendMessage({'call' : 'get_surfaces_by_app_details',
                                     'name' : str(name),
                                     'number' : str(instance)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def becomeSurfaceAdmin(self, surfaceNo):
        self.sendMessage({'call' : 'become_surface_admin',
                          'surfaceNo' : str(surfaceNo)})
        
    def stopBeingSurfaceAdmin(self, surfaceNo):
        self.sendMessage({'call' : 'stop_being_surface_admin',
                          'surfaceNo' : str(surfaceNo)})
        
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
        self.sendMessage({'call' : 'set_surface_edges',
                          'surfaceNo' : str(surfaceNo),
                          'topString' : topString,
                          'bottomString' : bottomString,
                          'leftString' : leftString,
                          'rightString' : rightString})
        
    def undefineSurface(self, surfaceNo):
        self.sendMessage({'call' : 'undefine_surface',
                          'surfaceNo' : str(surfaceNo)})
        
    def saveDefinedSurfaces(self, filename):
        self.sendMessage({'call' : 'save_defined_surfaces',
                          'fileName' : str(filename)})
        
    def loadDefinedSurfaces(self, filename):
        count = self.sendMessage({'call' : 'load_defined_surfaces',
                                  'fileName' : str(filename)})
        surfaces = count["layouts"].split("%")
        surfaceslist = []
        for x in range(0,len(surfaces)):
            sides = surfaces[x].split("&")
            sideslist = []
            for y in range(0,4):
                points = sides[y].split(";")
                side = []
                for z in range(0,len(points)):
                    point = points[z].split(":")
                    side.append((float(point[0]), float(point[1])))
                sideslist.append(side)
            surfaceslist.append(sideslist)
        if(count["connections"]!=""):
            connections = count["connections"].split("%")
            connectionslist = []
            for x in range(0,len(connections)):
                connection = connections[x].split(";")
                conn1 = connection[0].split(":")
                conn2 = connection[1].split(":")
                conn1list = [int(conn1[0]),conn1[1]]
                conn2list = [int(conn2[0]),conn2[1]]
                connectionslist.append([conn1list,conn2list])
            return (int(count["count"]),surfaceslist,connectionslist)
        else:
            return (int(count["count"]),surfaceslist,[])
        
    def getSavedLayouts(self):
        layouts = self.sendMessage({'call' : 'get_saved_layouts'})
        layoutlist = []
        for x in range(0,int(layouts['count'])):
            layoutlist.append(layouts[str(x)])
        return layoutlist
    
    def getSavedImages(self):
        images = self.sendMessage({'call' : 'get_saved_images'})
        imagelist = []
        for x in range(0,int(images['count'])):
            imagelist.append(images[str(x)])
        return imagelist
    
    def setSurfacePixelHeight(self,surfaceNo,height):
        self.sendMessage({'call' : 'set_surface_pixel_height',
                          'surfaceNo' : str(surfaceNo),
                          'height' : str(height)})
        
    def setSurfacePixelWidth(self,surfaceNo,width):
        self.sendMessage({'call' : 'set_surface_pixel_width',
                          'surfaceNo' : str(surfaceNo),
                          'width' : str(width)})
        
    def getSurfacePixelHeight(self,surfaceNo):
        height = self.sendMessage({'call' : 'get_surface_pixel_height',
                                   'surfaceNo' : str(surfaceNo)})
        return height["height"]
        
    def getSurfacePixelWidth(self,surfaceNo):
        width = self.sendMessage({'call' : 'get_surface_pixel_width',
                                  'surfaceNo' : str(surfaceNo)})
        return width["width"]
    
    def clearSurface(self,surfaceNo):
        self.sendMessage({'call' : 'clear_surface',
                          'surfaceNo' : str(surfaceNo)})
    
    def deleteLayout(self, name):
        self.sendMessage({'call' : 'delete_layout',
                          'name' : name})
        
    def deleteImage(self, filename):
        self.sendMessage({'call' : 'delete_image',
                          'filename' : filename})
        
    def rotateSurfaceTo0(self, surfaceNo):
        self.sendMessage({'call' : 'rotate_surface_to_0',
                          'surfaceNo' : str(surfaceNo)})
    
    def rotateSurfaceTo90(self, surfaceNo):
        self.sendMessage({'call' : 'rotate_surface_to_90',
                          'surfaceNo' : str(surfaceNo)})
    
    def rotateSurfaceTo180(self, surfaceNo):
        self.sendMessage({'call' : 'rotate_surface_to_180',
                          'surfaceNo' : str(surfaceNo)})
    
    def rotateSurfaceTo270(self, surfaceNo):
        self.sendMessage({'call' : 'rotate_surface_to_270',
                          'surfaceNo' : str(surfaceNo)})
    
    def mirrorSurface(self, surfaceNo):
        self.sendMessage({'call' : 'mirror_surface',
                          'surfaceNo' : str(surfaceNo)})
        
    def connectSurfaces(self, surfaceNo1, side1, surfaceNo2, side2):
        self.sendMessage({'call' : 'connect_surfaces',
                          'surfaceNo1' : str(surfaceNo1),
                          'side1' : side1,
                          'surfaceNo2' : str(surfaceNo2),
                          'side2' : side2})
    
    def disconnectSurfaces(self, surfaceNo1, side1, surfaceNo2, side2):
        self.sendMessage({'call' : 'disconnect_surfaces',
                          'surfaceNo1' : str(surfaceNo1),
                          'side1' : side1,
                          'surfaceNo2' : str(surfaceNo2),
                          'side2' : side2})
        
    def subscribeToWindow(self, windowNo):
        self.sendMessage({'call' : 'subscribe_to_window',
                          'windowNo' : str(windowNo)})
        
    def getWindowID(self, windowNo):
        ID = self.sendMessage({'call' : 'get_window_ID',
                               'windowNo' : str(windowNo)})
        return ID["ID"]
    
    def setWindowID(self, windowNo, ID):
        self.sendMessage({'call' : 'set_window_ID',
                          'windowNo' : str(windowNo),
                          'ID' : str(ID)})
    
    def getWindowOwner(self, windowNo):
        owner = self.sendMessage({'call' : 'get_window_owner',
                                  'windowNo' : str(windowNo)})
        return owner["owner"]
        
    def getWindowAppDetails(self, surfaceNo):
        details = self.sendMessage({'call' : 'get_window_app_details',
                                    'surfaceNo' : str(surfaceNo)})
        return (details["app"],details["instance"])
        
    def getWindowsByID(self, ID):
        windows = self.sendMessage({'call' : 'get_windows_by_ID',
                                    'ID' : str(ID)})
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def getWindowsByOwner(self, owner):
        windows = self.sendMessage({'call' : 'get_windows_by_owner',
                                    'owner' : str(owner)})
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def getWindowsByAppName(self, name):
        windows = self.sendMessage({'call' : 'get_windows_by_app_name',
                                    'name' : str(name)})
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def getWindowssByAppDetails(self, name, instance):
        windows = self.sendMessage({'call' : 'get_windows_by_app_details',
                                    'name' : str(name),
                                    'number' : str(instance)})
        windowlist = []
        for x in range(0,int(windows["count"])):
            windowlist.append(int(windows[x]))
        return windowlist
        
    def becomeWindowAdmin(self, windowNo):
        self.sendMessage({'call' : 'become_window_admin',
                          'windowNo' : str(windowNo)})
        
    def stopBeingWindowAdmin(self, windowNo):
        self.sendMessage({'call' : 'stop_being_window_admin', 
                          'windowNo' : str(windowNo)})
        
    def subscribeToElement(self, elementNo):
        self.sendMessage({'call' : 'subscribe_to_element',
                          'elementNo' : str(elementNo)})
        
    def getElementID(self, elementNo):
        ID = self.sendMessage({'call' : 'get_element_ID', 
                               'elementNo' : str(elementNo)})
        return ID["ID"]
    
    def setElementID(self, elementNo, ID):
        self.sendMessage({'call' : 'set_element_ID',
                          'elementNo' : str(elementNo),
                          'ID' : str(ID)})
    
    def getElementOwner(self, elementNo):
        owner = self.sendMessage({'call' : 'get_element_owner',
                                  'elementNo' : str(elementNo)})
        return owner["owner"]
        
    def getElementAppDetails(self, surfaceNo):
        details = self.sendMessage({'call' : 'get_element_app_details',
                                    'surfaceNo' : str(surfaceNo)})
        return (details["app"],details["instance"])
        
    def getElementsByID(self, ID):
        elements = self.sendMessage({'call' : 'get_elements_by_ID',
                                     'ID' : str(ID)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByOwner(self, owner):
        elements = self.sendMessage({'call' : 'get_elements_by_owner',
                                     'owner' : str(owner)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByAppName(self, name):
        elements = self.sendMessage({'call' : 'get_elements_by_app_name',
                                     'name' : str(name)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByAppDetails(self, name, instance):
        elements = self.sendMessage({'call' : 'get_elements_by_app_details',
                                     'name' : str(name),
                                     'number' : str(instance)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
    
    def getElementsOnWindow(self, windowNo):
        elements = self.sendMessage({'call' : 'get_elements_on_window',
                                     'windowNo' : str(windowNo)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def becomeElementAdmin(self, elementNo):
        self.sendMessage({'call' : 'become_element_admin',
                         'elementNo' : str(elementNo)})
        
    def stopBeingElementAdmin(self, elementNo):
        self.sendMessage({'call' : 'stop_being_element_admin',
                          'elementNo' : str(elementNo)})
    
    def moveCursor(self, cursorNo, xDistance, yDistance):
        self.sendMessage({'call' : 'move_cursor',
                          'cursorNo' : str(cursorNo),
                          'xDist' : str(xDistance),
                          'yDist' : str(yDistance)})
        
    def testMoveCursor(self, cursorNo, xDistance, yDistance):
        loc = self.sendMessage({'call' : 'test_move_cursor',
                                'cursorNo' : str(cursorNo),
                                'xDist' : str(xDistance),
                                'yDist' : str(yDistance)})
        return [loc["x"],loc["y"]]
    
    def relocateCursor(self, cursorNo, x, y, surfaceNo):
        self.sendMessage({'call' : 'relocate_cursor',
                          'cursorNo' : str(cursorNo),
                          'x' : str(x),
                          'y' : str(y),
                          'surfaceNo' : str(surfaceNo)})
    
    def getCursorPosition(self, cursorNo):
        loc = self.sendMessage({'call' : 'get_cursor_pos',
                                'cursorNo' : str(cursorNo)})
        return [loc["x"],loc["y"]]
    
    def rotateCursorClockwise(self, cursorNo, degrees):
        self.sendMessage({'call' : 'rotate_cursor_clockwise',
                          'cursorNo' : str(cursorNo),
                          'degrees' : str(degrees)})

    def rotateCursorAnticlockwise(self, cursorNo, degrees):
        self.sendMessage({'call' : 'rotate_cursor_anticlockwise',
                          'cursorNo' : str(cursorNo),
                          'degrees' : str(degrees)})
    
    def getCursorRotation(self, cursorNo):
        rotation = self.sendMessage({'call' : 'get_cursor_rotation',
                                     'cursorNo' : str(cursorNo)})
        return rotation["rotation"]
    
    def getCursorMode(self, cursorNo):
        mode = self.sendMessage({'call' : 'get_cursor_mode',
                                 'cursorNo' : str(cursorNo)})
        return mode["mode"]
    
    def setCursorDefaultMode(self, cursorNo):
        self.sendMessage({'call' : 'set_cursor_default_mode',
                          'cursorNo' : str(cursorNo)})
        
    def setCursorWallMode(self, cursorNo):
        self.sendMessage({'call' : 'set_cursor_wall_mode',
                          'cursorNo' : str(cursorNo)})
        
    def setCursorBlockMode(self, cursorNo):
        self.sendMessage({'call' : 'set_cursor_block_mode',
                          'cursorNo' : str(cursorNo)})
        
    def setCursorScreenMode(self, cursorNo):
        self.sendMessage({'call' : 'set_cursor_screen_mode',
                          'cursorNo' : str(cursorNo)})
        
    def showCursor(self, cursorNo):
        self.sendMessage({'call' : 'show_cursor',
                          'cursorNo' : str(cursorNo)})
    
    def hideCursor(self, cursorNo):
        self.sendMessage({'call' : 'hide_cursor',
                          'cursorNo' : str(cursorNo)})
    
    def isCursorVisible(self, cursorNo):
        visibility = self.sendMessage({'call' : 'isCursorVisible',
                                       'cursorNo' : str(cursorNo)})
        return visibility["visibility"]
    
    def moveWindow(self, windowNo, xDistance, yDistance):
        self.sendMessage({'call' : 'move_window',
                          'windowNo' : str(windowNo),
                          'xDist' : str(xDistance),
                          'yDist' : str(yDistance)})
        
    def relocateWindow(self, windowNo, x, y, surfaceNo):
        self.sendMessage({'call' : 'relocate_window',
                          'windowNo' : str(windowNo),
                          'x' : str(x),
                          'y' : str(y),
                          'surfaceNo' : str(surfaceNo)})
        
    def setWindowWidth(self, windowNo, width):
        self.sendMessage({'call' : 'set_window_width',
                          'windowNo' : str(windowNo),
                          'width' : str(width)})
        
    def setWindowHeight(self, windowNo, height):
        self.sendMessage({'call' : 'set_window_height',
                          'windowNo' : str(windowNo),
                          'height' : str(height)})
        
    def getWindowPosition(self, windowNo):
        loc = self.sendMessage({'call' : 'get_window_pos',
                                'windowNo' : str(windowNo)})
        return [loc["x"],loc["y"]]
        
    def getWindowWidth(self, windowNo):
        width = self.sendMessage({'call' : 'get_window_width',
                                  'windowNo' : str(windowNo)})
        return width["width"]
        
    def getWindowHeight(self, windowNo):
        height = self.sendMessage({'call' : 'get_window_height',
                                   'windowNo' : str(windowNo)})
        return height["height"]
        
    def stretchWindowDown(self, windowNo, distance):
        self.sendMessage({'call' : 'stretch_window_down',
                          'windowNo' : str(windowNo),
                          'distance' : str(distance)})
        
    def stretchWindowUp(self, windowNo, distance):
        self.sendMessage({'call' : 'stretch_window_up',
                          'windowNo' : str(windowNo),
                          'distance' : str(distance)})
        
    def stretchWindowLeft(self, windowNo, distance):
        self.sendMessage({'call' : 'stretch_window_left',
                          'windowNo' : str(windowNo),
                          'distance' : str(distance)})
        
    def stretchWindowRight(self, windowNo, distance):
        self.sendMessage({'call' : 'stretch_window_right',
                          'windowNo' : str(windowNo),
                          'distance' : str(distance)})
        
    def setWindowName(self, windowNo, name):
        self.sendMessage({'call' : 'set_window_name',
                          'windowNo' : str(windowNo),
                          'name' : name})
        
    def getWindowName(self, windowNo):
        name = self.sendMessage({'call' : 'get_window_name',
                                 'windowNo' : str(windowNo)})
        return name["name"]
    
    def relocateCircle(self, elementNo, x, y, windowNo):
        self.elelocs[elementNo] = (x,y)
        self.eletrack[elementNo][0] = True
        
    def getCirclePosition(self, elementNo):
        if (self.elelocs.has_key(elementNo)):
            return [self.elelocs[elementNo][0],self.elelocs[elementNo][1]]
        else:
            loc = self.sendMessage({'call' : 'get_circle_pos',
                                    'elementNo' : str(elementNo)})
            return [loc["x"],loc["y"]]
    
    def getElementType(self, elementNo):
        type = self.sendMessage({'call' : 'get_element_type',
                                 'elementNo' : str(elementNo)})
        return type["type"]
    
    def setCircleLineColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_circle_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setCircleLineWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_circle_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def setCircleFillColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_circle_fill_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})

    def getCircleLineColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_circle_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def getCircleLineWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_circle_line_width',
                                 'elementNo' : str(elementNo)})
        return width["width"]
        
    def getCircleFillColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_circle_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setCircleRadius(self, elementNo, radius):
        self.sendMessage({'call' : 'set_circle_radius',
                          'elementNo' : str(elementNo),
                          'radius' : str(radius)})
        
    def getCircleRadius(self, elementNo):
        radius = self.sendMessage({'call' : 'get_circle_radius',
                                   'elementNo' : str(elementNo)})
        return radius["radius"]
    
    def setCircleSides(self, elementNo, sides):
        self.sendMessage({'call' : 'set_circle_sides',
                          'elementNo' : str(elementNo),
                          'sides' : str(sides)})
        
    def getCircleSides(self, elementNo):
        sides = self.sendMessage({'call' : 'get_circle_sides',
                                  'elementNo' : str(elementNo)})
        return sides["sides"]
    
    def getLineStart(self, elementNo):
        loc = self.sendMessage({'call' : 'get_line_start',
                                'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
    
    def getLineEnd(self, elementNo):
        loc = self.sendMessage({'call' : 'get_line_end',
                                'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
    
    def setLineStart(self, elementNo, x, y):
        self.sendMessage({'call' : 'relocate_line_start',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y)})
    
    def setLineEnd(self, elementNo, x, y):
        self.sendMessage({'call' : 'relocate_line_end',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y)})
    
    def setLineColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getLineColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setLineWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getLineWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_line_width',
                                  'elementNo' : str(elementNo)})
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
            loc = self.sendMessage({'call' : 'get_line_strip_point',
                                    'elementNo' : str(elementNo),
                                    'index' : str(pointNo)})
            return [loc["x"],loc["y"]]
    
    def moveLineStripPoint(self, elementNo, pointNo, x, y):
        self.stripLock.acquire()
        self.elelocs[elementNo][pointNo] = [x,y]
        self.eletrack[elementNo][0] = True
        self.stripLock.release()
        
    def getLineStripColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_line_strip_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def setLineStripColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_line_strip_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setLineStripWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_line_strip_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getLineStripWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_line_strip_width',
                                  'elementNo' : str(elementNo)})
        return width["width"]
        
    def getLineStripPointCount(self, elementNo):
        count = self.sendMessage({'call' : 'get_line_strip_point_count',
                                  'elementNo' : str(elementNo)})
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
        self.sendMessage({'call' : 'add_polygon_point',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y)})
        
    def getPolygonPoint(self, elementNo, pointNo):
        loc = self.sendMessage({'call' : 'get_polygon_point',
                                'elementNo' : str(elementNo),
                                'index' : str(pointNo)})
        return (loc["x"],loc["y"])
    
    def movePolygonPoint(self, elementNo, pointNo, x, y):
        self.sendMessage({'call' : 'relocate_polygon_point',
                          'elementNo' : str(elementNo),
                          'index' : str(pointNo),
                          'x' : str(x),
                          'y' : str(y)})
        
    def getPolygonFillColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_polygon_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setPolygonFillColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_polygon_fill_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getPolygonLineColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_polygon_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def getPolygonLineWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_polygon_line_width',
                                 'elementNo' : str(elementNo)})
        return width["width"]
    
    def setPolygonLineColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_polygon_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setPolygonLineWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_polygon_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getPolygonPointCount(self, elementNo):
        count = self.sendMessage({'call' : 'get_polygon_point_count',
                                  'elementNo' : str(elementNo)})
        return count["count"]
    
    def setRectangleTopLeft(self, elementNo, x, y):
        self.sendMessage({'call' : 'set_rectangle_top_left',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y)})
        
    def getRectangleTopLeft(self, elementNo):
        pos = self.sendMessage({'call' : 'get_rectangle_top_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleTopRight(self, elementNo):
        pos = self.sendMessage({'call' : 'get_rectangle_top_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleBottomRight(self, elementNo):
        pos = self.sendMessage({'call' : 'get_rectangle_bottom_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleBottomLeft(self, elementNo):
        pos = self.sendMessage({'call' : 'get_rectangle_bottom_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def setRectangleWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_rectangle_width',
                         'elementNo' : str(elementNo),
                         'width' : str(width)})
        
    def getRectangleWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_rectangle_width',
                                  'elementNo' : str(elementNo)})
        return float(width["width"])
        
    def setRectangleHeight(self, elementNo, height):
        self.sendMessage({'call' : 'set_rectangle_height',
                          'elementNo' : str(elementNo),
                          'height' : str(height)})
        
    def getRectangleHeight(self, elementNo):
        height = self.sendMessage({'call' : 'get_rectangle_height',
                                   'elementNo' : str(elementNo)})
        return float(height["height"])
    
    def setRectangleFillColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_rectangle_fill_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getRectangleFillColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_rectangle_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setRectangleLineColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_rectangle_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setRectangleLineWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_rectangle_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getRectangleLineColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_rectangle_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def getRectangleLineWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_rectangle_line_width',
                                 'elementNo' : str(elementNo)})
        return width["width"]
    
    def setTexRectangleTopLeft(self, elementNo, x, y):
        self.sendMessage({'call' : 'set_texrectangle_top_left',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y)})
        
    def getTexRectangleTopLeft(self, elementNo):
        pos = self.sendMessage({'call' : 'get_texrectangle_top_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleTopRight(self, elementNo):
        pos = self.sendMessage({'call' : 'get_texrectangle_top_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleBottomRight(self, elementNo):
        pos = self.sendMessage({'call' : 'get_texrectangle_bottom_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleBottomLeft(self, elementNo):
        pos = self.sendMessage({'call' : 'get_texrectangle_bottom_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleTexture(self, elementNo):
        tex = self.sendMessage({'call' : 'get_texrectangle_texture',
                                'elementNo' : str(elementNo)})
        return tex["texture"]
    
    def setTexRectangleTexture(self, elementNo, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            self.sendMessage({'call' : 'set_texrectangle_texture',
                              'elementNo' : str(elementNo),
                              'textureData' : encoded_string,
                              'extension' : extension})
    
    def setTexRectangleWidth(self, elementNo, width):
        self.sendMessage({'call' : 'set_texrectangle_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getTexRectangleWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_texrectangle_width',
                                  'elementNo' : str(elementNo)})
        return float(width["width"])
        
    def setTexRectangleHeight(self, elementNo, height):
        self.sendMessage({'call' : 'set_texrectangle_height',
                          'elementNo' : str(elementNo),
                          'height' : str(height)})
        
    def getTexRectangleHeight(self, elementNo):
        height = self.sendMessage({'call' : 'get_texrectangle_height',
                                   'elementNo' : str(elementNo)})
        return float(height["height"])
    
    def setText(self, elementNo, text):
        self.sendMessage({'call' : 'set_text',
                          'elementNo' : str(elementNo),
                          'text' : text})
        
    def getText(self, elementNo):
        text = self.sendMessage({'call' : 'get_text',
                                 'elementNo' : str(elementNo)})
        return text["text"]
    
    def setTextPosition(self, elementNo, x, y, windowNo):
        self.sendMessage({'call' : 'relocate_text',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'windowNo' : str(windowNo)})
        
    def getTextPosition(self, elementNo):
        loc = self.sendMessage({'call' : 'get_text_pos',
                                'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
        
    def setPointSize(self, elementNo, pointSize):
        self.sendMessage({'call' : 'set_text_point_size',
                          'elementNo' : str(elementNo),
                          'pt' : str(pointSize)})
        
    def getPointSize(self, elementNo):
        size = self.sendMessage({'call' : 'get_text_point_size',
                                 'elementNo' : str(elementNo)})
        return size["size"]
    
    def getFont(self, elementNo):
        font = self.sendMessage({'call' : 'get_text_font',
                                 'elementNo' : str(elementNo)})
        return font["font"]
    
    def setFont(self, elementNo, font):
        self.sendMessage({'call' : 'set_text_font',
                          'elementNo' : str(elementNo),
                          'font' : font})
        
    def setTextColor(self, elementNo, color):
        self.sendMessage({'call' : 'set_text_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getTextColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_text_color',
                                                 'elementNo' : str(elementNo)})["color"])
           
    def showElement(self, elementNo):
        self.sendMessage({'call' : 'show_element',
                         'elementNo' : str(elementNo)})
        
    def hideElement(self, elementNo):
        self.sendMessage({'call' : 'hide_element',
                          'elementNo' : str(elementNo)})
        
    def checkElementVisibility(self, elementNo):
        visibility = self.sendMessage({'call' : 'check_element_visibility',
                                       'elementNo' : str(elementNo)})
        return visibility["visible"]
        
    def hideSetupSurface(self):
        self.sendMessage({'call' : 'hide_setup_surface'})
        
    def showSetupSurface(self):
        self.sendMessage({'call' : 'show_setup_surface'})
        
    def getSetupSurfaceVisibility(self):
        return self.sendMessage({'call' : 'get_setup_surface_visibility'})
        
    def getClickedElements(self, surfaceNo, x, y):
        elements = self.sendMessage({'call' : 'get_clicked_elements',
                                     'surfaceNo' : str(surfaceNo),
                                     'x' : str(x),
                                     'y' : str(y)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
    
    def removeElement(self, elementNo, windowNo):
        self.sendMessage({'call' : 'remove_element',
                          'elementNo' : str(elementNo),
                          'windowNo' : str(windowNo)})