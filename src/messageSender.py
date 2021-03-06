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
    stripLock = threading.Lock()
    sendlock = threading.Lock()
    loop = True
    
    def encode_length(self, l):
        l = str(l)
        while len(l) < 8:
            l = "0" + l
        return l

    def uploadImage(self, fileParam):
        filename = fileParam.split("/")
        filename = filename[-1]
        self.sendMessage({'call' : 'set_upload_name', 'filename' : filename})
        time.sleep(0.5)
        s = socket.socket()
        s.connect((self.host,self.port+1))
        imageNo = s.recv(1024)
        
        f=open(fileParam, "rb") 
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
    
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        self.refreshrate = 1/(parser.getint('library','MovesPerSecond'))
        self.host = parser.get('connection','host')
        self.port = parser.getint('connection','port')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.settimeout(2)
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
        socket_list = [self.s]
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
        
    def quitClientOnly(self):
        self.loop=False
        
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
    
    def newCursor(self, surfaceNo, x, y, coorSys):
        cur = self.sendMessage({'call' : 'new_cursor', 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' : str(y),
                                'coorSys' : coorSys})
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newCursorWithID(self, ID, surfaceNo, x, y, coorSys):
        cur = self.sendMessage({'call' : 'new_cursor_with_ID', 
                                'ID' : str(ID), 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' : str(y),
                                'coorSys' : coorSys})
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newCanvas(self, surfaceNo, x, y, width, height, coorSys, name):
        win = self.sendMessage({'call' : 'new_canvas', 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' :  str(y), 
                                'width' : str(width), 
                                'height' : str(height),
                                'coorSys' : coorSys,
                                'name' : name})
        winNo = int(win["canvasNo"])
        return winNo
    
    def newCanvasWithID(self, ID, surfaceNo, x, y, width, height, coorSys, name):
        win = self.sendMessage({'call' : 'new_canvas_with_ID', 
                                'ID' : str(ID), 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' :  str(y), 
                                'width' : str(width), 
                                'height' : str(height),
                                'coorSys' : coorSys,
                                'name' : name})
        winNo = int(win["canvasNo"])
        return winNo
    
    def newCircle(self, canvasNo, x, y, radius, coorSys, lineCol, lineWidth, fillCol, sides):
        ele = self.sendMessage({'call' : 'new_circle', 
                                'canvasNo' :  str(canvasNo), 
                                'x' : str(x), 
                                'y' : str(y), 
                                'radius' : str(radius),
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineCol[0], lineCol[1], lineCol[2], lineCol[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillCol[0], fillCol[1], fillCol[2], fillCol[3]), 
                                'sides' : str(sides)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newCircleWithID(self, ID, canvasNo, x, y, radius, coorSys, lineCol, lineWidth, fillCol, sides):
        ele = self.sendMessage({'call' : 'new_circle_with_ID',
                                'ID' : str(ID),
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'radius' : str(radius), 
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineCol[0], lineCol[1], lineCol[2], lineCol[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillCol[0], fillCol[1], fillCol[2], fillCol[3]),
                                'sides' : str(sides)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newLine(self, canvasNo, xStart, yStart, xEnd, yEnd, coorSys, color, width):
        ele = self.sendMessage({'call' : 'new_line',
                                'canvasNo' : str(canvasNo),
                                'xStart' : str(xStart),
                                'yStart' : str(yStart),
                                'xEnd' : str(xEnd),
                                'yEnd' : str(yEnd),
                                'coorSys' : coorSys,
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newLineWithID(self, ID, canvasNo, xStart, yStart, xEnd, yEnd, coorSys, color, width):
        ele = self.sendMessage({'call' : 'new_line_with_ID',
                                'ID' : str(ID),
                                'canvasNo' : str(canvasNo),
                                'xStart' : str(xStart),
                                'yStart' : str(yStart),
                                'xEnd' : str(xEnd),
                                'yEnd' : str(yEnd),
                                'coorSys' : coorSys,
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newLineStrip(self, canvasNo, x, y, coorSys, color, width):
        ele = self.sendMessage({'call' : 'new_line_strip', 
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newLineStripWithID(self, ID, canvasNo, x, y, coorSys, color, width):
        ele = self.sendMessage({'call' : 'new_line_strip_with_ID',
                                'ID' : str(ID), 
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newPolygon(self, canvasNo, x, y, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_polygon',
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newPolygonWithID(self, ID, canvasNo, x, y, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_polygon_with_ID',
                                'ID' : str(ID),
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newTexRectangle(self, canvasNo, x, y, width, height, coorSys, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ele = self.sendMessage({'call' : 'new_texrectangle',
                                    'canvasNo' : str(canvasNo),
                                    'x' : str(x),
                                    'y' : str(y),
                                    'width' : str(width),
                                    'height' : str(height),
                                    'coorSys' : coorSys,
                                    'textureData' : encoded_string,
                                    'extension' : extension})
            eleNo = int(ele["elementNo"])
            return eleNo
    
    def newTexRectangleWithID(self, ID, canvasNo, x, y, width, height, coorSys, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ele = self.sendMessage({'call' : 'new_texrectangle_with_ID',
                                    'ID' : str(ID),
                                    'canvasNo' : str(canvasNo),
                                    'x' : str(x),
                                    'y' : str(y),
                                    'width' : str(width),
                                    'height' : str(height),
                                    'coorSys' : coorSys,
                                    'textureData' : encoded_string,
                                    'extension' : extension})
            eleNo = int(ele["elementNo"])
            return eleNo
    
    def newRectangle(self, canvasNo, x, y, width, height, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_rectangle',
                                'canvasNo' : str(canvasNo), 
                                'x' : str(x),
                                'y' : str(y),
                                'width' : str(width),
                                'height' : str(height),
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newRectangleWithID(self, ID, canvasNo, x, y, width, height, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage({'call' : 'new_rectangle_with_ID',
                                'ID' : str(ID),
                                'canvasNo' : str(canvasNo), 
                                'x' : str(x),
                                'y' : str(y),
                                'width' : str(width),
                                'height' : str(height),
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newText(self, canvasNo, text, x, y, coorSys, ptSize, font, color):
        ele = self.sendMessage({'call' : 'new_text',
                                'canvasNo' : str(canvasNo),
                                'text' : text,
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'ptSize' : str(ptSize),
                                'font' : font,
                                'color' : self.colorString(color[0], color[1], color[2], color[3])})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newTextWithID(self, ID, canvasNo, text, x, y, coorSys, ptSize, font, color):
        ele = self.sendMessage({'call' : 'new_text_with_ID',
                                'ID' : str(ID),
                                'canvasNo' : str(canvasNo),
                                'text' : text,
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'pt' : str(ptSize),
                                'font' : font,
                                'color' : self.colorString(color[0], color[1], color[2], color[3])})
        eleNo = int(ele["elementNo"])
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
        realSizes = count["realSizes"]
        realSizes = realSizes.split(";")
        for x in range(0,len(realSizes)):
            realSizes[x] = realSizes[x].split(":")
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
            return (int(count["count"]),surfaceslist,connectionslist, realSizes)
        else:
            return (int(count["count"]),surfaceslist,[], realSizes)
        
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
        return float(height["height"])
        
    def getSurfacePixelWidth(self,surfaceNo):
        width = self.sendMessage({'call' : 'get_surface_pixel_width',
                                  'surfaceNo' : str(surfaceNo)})
        return float(width["width"])
    
    def setSurfaceRealHeight(self,surfaceNo,height):
        self.sendMessage({'call' : 'set_surface_real_height',
                          'surfaceNo' : str(surfaceNo),
                          'height' : str(height)})
        
    def setSurfaceRealWidth(self,surfaceNo,width):
        self.sendMessage({'call' : 'set_surface_real_width',
                          'surfaceNo' : str(surfaceNo),
                          'width' : str(width)})
        
    def getSurfaceRealHeight(self,surfaceNo):
        height = self.sendMessage({'call' : 'get_surface_real_height',
                                   'surfaceNo' : str(surfaceNo)})
        return float(height["height"])
        
    def getSurfaceRealWidth(self,surfaceNo):
        width = self.sendMessage({'call' : 'get_surface_real_width',
                                  'surfaceNo' : str(surfaceNo)})
        return float(width["width"])
    
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
        
    def subscribeToCanvas(self, canvasNo):
        self.sendMessage({'call' : 'subscribe_to_canvas',
                          'canvasNo' : str(canvasNo)})
        
    def getCanvasID(self, canvasNo):
        ID = self.sendMessage({'call' : 'get_canvas_ID',
                               'canvasNo' : str(canvasNo)})
        return ID["ID"]
    
    def setCanvasID(self, canvasNo, ID):
        self.sendMessage({'call' : 'set_canvas_ID',
                          'canvasNo' : str(canvasNo),
                          'ID' : str(ID)})
    
    def getCanvasOwner(self, canvasNo):
        owner = self.sendMessage({'call' : 'get_canvas_owner',
                                  'canvasNo' : str(canvasNo)})
        return owner["owner"]
        
    def getCanvasAppDetails(self, canvasNo):
        details = self.sendMessage({'call' : 'get_canvas_app_details',
                                    'canvasNo' : str(canvasNo)})
        return (details["app"],details["instance"])
        
    def getCanvasesByID(self, ID):
        canvases = self.sendMessage({'call' : 'get_canvases_by_ID',
                                    'ID' : str(ID)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def getCanvasesByOwner(self, owner):
        canvases = self.sendMessage({'call' : 'get_canvases_by_owner',
                                    'owner' : str(owner)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def getCanvasesByAppName(self, name):
        canvases = self.sendMessage({'call' : 'get_canvases_by_app_name',
                                    'name' : str(name)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def getCanvasesByAppDetails(self, name, instance):
        canvases = self.sendMessage({'call' : 'get_canvases_by_app_details',
                                    'name' : str(name),
                                    'number' : str(instance)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def becomeCanvasAdmin(self, canvasNo):
        self.sendMessage({'call' : 'become_canvas_admin',
                          'canvasNo' : str(canvasNo)})
        
    def stopBeingCanvasAdmin(self, canvasNo):
        self.sendMessage({'call' : 'stop_being_canvas_admin', 
                          'canvasNo' : str(canvasNo)})
        
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
    
    def getElementsOnCanvas(self, canvasNo):
        elements = self.sendMessage({'call' : 'get_elements_on_canvas',
                                     'canvasNo' : str(canvasNo)})
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
    
    def shiftCursor(self, cursorNo, xDistance, yDistance):
        self.sendMessage({'call' : 'move_cursor',
                          'cursorNo' : str(cursorNo),
                          'xDist' : str(xDistance),
                          'yDist' : str(yDistance)})
        
    def testShiftCursor(self, cursorNo, xDistance, yDistance):
        loc = self.sendMessage({'call' : 'test_move_cursor',
                                'cursorNo' : str(cursorNo),
                                'xDist' : str(xDistance),
                                'yDist' : str(yDistance)})
        return [float(loc["x"]),float(loc["y"])]
    
    def relocateCursor(self, cursorNo, x, y, coorSys, surfaceNo):
        self.sendMessage({'call' : 'relocate_cursor',
                          'cursorNo' : str(cursorNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'surfaceNo' : str(surfaceNo)})
    
    def getCursorPosition(self, cursorNo):
        loc = self.sendMessage({'call' : 'get_cursor_pos',
                                'cursorNo' : str(cursorNo)})
        return [float(loc["x"]),float(loc["y"])]
    
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
        return float(rotation["rotation"])
    
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

    def getCursorsSurface(self, cursorNo):
        surfaceNo = self.sendMessage({'call' : 'get_cursors_surface',
                                      'cursorNo' : str(cursorNo)})
        return int(surfaceNo["surfaceNo"])
    
    def isCursorVisible(self, cursorNo):
        visibility = self.sendMessage({'call' : 'isCursorVisible',
                                       'cursorNo' : str(cursorNo)})
        return bool(visibility["visibility"])
    
    def shiftCanvas(self, canvasNo, xDistance, yDistance, coorSys):
        self.sendMessage({'call' : 'move_canvas',
                          'canvasNo' : str(canvasNo),
                          'xDist' : str(xDistance),
                          'yDist' : str(yDistance),
                          'coorSys' : str(coorSys)})
        
    def relocateCanvas(self, canvasNo, x, y, coorSys, surfaceNo):
        self.sendMessage({'call' : 'relocate_canvas',
                          'canvasNo' : str(canvasNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'surfaceNo' : str(surfaceNo)})
        
    def setCanvasWidth(self, canvasNo, width, coorSys):
        self.sendMessage({'call' : 'set_canvas_width',
                          'canvasNo' : str(canvasNo),
                          'width' : str(width),
                          'coorSys' : str(coorSys)})
        
    def setCanvasHeight(self, canvasNo, height, coorSys):
        self.sendMessage({'call' : 'set_canvas_height',
                          'canvasNo' : str(canvasNo),
                          'height' : str(height),
                          'coorSys' : str(coorSys)})
        
    def getCanvasPosition(self, canvasNo):
        loc = self.sendMessage({'call' : 'get_canvas_pos',
                                'canvasNo' : str(canvasNo)})
        return [float(loc["x"]),float(loc["y"])]
        
    def getCanvasWidth(self, canvasNo):
        width = self.sendMessage({'call' : 'get_canvas_width',
                                  'canvasNo' : str(canvasNo)})
        return float(width["width"])
        
    def getCanvasHeight(self, canvasNo):
        height = self.sendMessage({'call' : 'get_canvas_height',
                                   'canvasNo' : str(canvasNo)})
        return float(height["height"])
        
    def stretchCanvasDown(self, canvasNo, distance, coorSys):
        self.sendMessage({'call' : 'stretch_canvas_down',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def stretchCanvasUp(self, canvasNo, distance, coorSys):
        self.sendMessage({'call' : 'stretch_canvas_up',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def stretchCanvasLeft(self, canvasNo, distance, coorSys):
        self.sendMessage({'call' : 'stretch_canvas_left',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def stretchCanvasRight(self, canvasNo, distance, coorSys):
        self.sendMessage({'call' : 'stretch_canvas_right',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def setCanvasName(self, canvasNo, name):
        self.sendMessage({'call' : 'set_canvas_name',
                          'canvasNo' : str(canvasNo),
                          'name' : name})
        
    def getCanvasName(self, canvasNo):
        name = self.sendMessage({'call' : 'get_canvas_name',
                                 'canvasNo' : str(canvasNo)})
        return name["name"]

    def getCanvasSurface(self, canvasNo):
        surfaceNo = self.sendMessage({'call' : 'get_canvas_surface',
                                      'canvasNo' : str(canvasNo)})
        return int(surfaceNo["surfaceNo"])
    
    def shiftCircle(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_circle',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocateCircle(self, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'relocate_circle', 
                          'elementNo' : elementNo, 
                          'x' : x, 
                          'y' : y, 
                          'coorSys' : coorSys,
                          'canvasNo' : canvasNo})
        
    def getCirclePosition(self, elementNo):
        loc = self.sendMessage({'call' : 'get_circle_pos',
                                    'elementNo' : str(elementNo)})
        return [float(loc["x"]),float(loc["y"])]
    
    def getElementType(self, elementNo):
        typeName = self.sendMessage({'call' : 'get_element_type',
                                 'elementNo' : str(elementNo)})
        return typeName["type"]

    def getElementsCanvas(self, elementNo):
        canvasNo = self.sendMessage({'call' : 'get_elements_canvas',
                                     'elementNo' : str(elementNo)})
        return int(canvasNo["canvasNo"])
    
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
        return float(width["width"])
        
    def getCircleFillColor(self, elementNo):
        return self.colorTuple(self.sendMessage({'call' : 'get_circle_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setCircleRadius(self, elementNo, radius, coorSys):
        self.sendMessage({'call' : 'set_circle_radius',
                          'elementNo' : str(elementNo),
                          'radius' : str(radius),
                          'coorSys' : str(coorSys)})
        
    def getCircleRadius(self, elementNo):
        radius = self.sendMessage({'call' : 'get_circle_radius',
                                   'elementNo' : str(elementNo)})
        return float(radius["radius"])
    
    def setCircleSides(self, elementNo, sides):
        self.sendMessage({'call' : 'set_circle_sides',
                          'elementNo' : str(elementNo),
                          'sides' : str(sides)})
        
    def getCircleSides(self, elementNo):
        sides = self.sendMessage({'call' : 'get_circle_sides',
                                  'elementNo' : str(elementNo)})
        return int(sides["sides"])
    
    def shiftLine(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_line',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocateLine(self, elementNo, refPoint, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'relocate_line',
                          'elementNo' : str(elementNo),
                          'refPoint' : str(refPoint),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
    
    def getLineStart(self, elementNo):
        loc = self.sendMessage({'call' : 'get_line_start',
                                'elementNo' : str(elementNo)})
        return [float(loc["x"]),float(loc["y"])]
    
    def getLineEnd(self, elementNo):
        loc = self.sendMessage({'call' : 'get_line_end',
                                'elementNo' : str(elementNo)})
        return [float(loc["x"]),float(loc["y"])]
    
    def setLineStart(self, elementNo, x, y, coorSys):
        self.sendMessage({'call' : 'relocate_line_start',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
    
    def setLineEnd(self, elementNo, x, y, coorSys):
        self.sendMessage({'call' : 'relocate_line_end',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
    
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
        return float(width["width"])
    
    def addLineStripPoint(self, elementNo, x, y, coorSys):
        self.sendMessage({'call' : 'add_line_strip_point',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : coorSys})
        
    def addLineStripPointAt(self, elementNo, x, y, coorSys, index):
        self.sendMessage({'call' : 'add_line_strip_point_at',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : coorSys,
                          'index' : str(index)})
        
    def getLineStripPoint(self, elementNo, pointNo):
        loc = self.sendMessage({'call' : 'get_line_strip_point',
                                'elementNo' : str(elementNo),
                                'index' : str(pointNo)})
        return [float(loc["x"]),float(loc["y"])]
        
    def shiftLineStrip(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_line_strip',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocateLineStrip(self, elementNo, refPoint, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'relocate_line_strip',
                          'elementNo' : str(elementNo),
                          'refPoint' : str(refPoint),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
    
    def moveLineStripPoint(self, elementNo, pointNo, x, y, coorSys):
        self.sendMessage({'call' : 'relocate_line_strip_point',
                          'elementNo' : str(elementNo),
                          'pointNo' : str(pointNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : coorSys})
        
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
        return float(width["width"])
        
    def getLineStripPointCount(self, elementNo):
        count = self.sendMessage({'call' : 'get_line_strip_point_count',
                                  'elementNo' : str(elementNo)})
        return int(count["count"])
    
    def setLineStripContent(self, elementNo, content):
        converted = str(content[0][0]) + ":" + str(content[0][1])
        for y in range(0,len(content)):
            converted += ";" + str(content[y][0]) + ":" + str(content[y][1])
        self.sendMessage({'call' : 'set_line_strip_content', 
                          'elementNo' : str(elementNo), 
                          'content' : converted})
    
    def addPolygonPoint(self, elementNo, x, y, coorSys):
        self.sendMessage({'call' : 'add_polygon_point',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
        
    def getPolygonPoint(self, elementNo, pointNo):
        loc = self.sendMessage({'call' : 'get_polygon_point',
                                'elementNo' : str(elementNo),
                                'index' : str(pointNo)})
        return (float(loc["x"]),float(loc["y"]))
    
    def shiftPolygon(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_polygon',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocatePolygon(self, elementNo, refPoint, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'relocate_polygon',
                          'elementNo' : str(elementNo),
                          'refPoint' : str(refPoint),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
    
    def movePolygonPoint(self, elementNo, pointNo, x, y, coorSys):
        self.sendMessage({'call' : 'relocate_polygon_point',
                          'elementNo' : str(elementNo),
                          'index' : str(pointNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
        
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
        return float(width["width"])
    
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
        return int(count["count"])
    
    def relocateRectangle(self, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'set_rectangle_top_left',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
        
    def shiftRectangle(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_rectangle',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
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
    
    def setRectangleWidth(self, elementNo, width, coorSys):
        self.sendMessage({'call' : 'set_rectangle_width',
                         'elementNo' : str(elementNo),
                         'width' : str(width),
                         'coorSys' : str(coorSys)})
        
    def getRectangleWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_rectangle_width',
                                  'elementNo' : str(elementNo)})
        return float(width["width"])
        
    def setRectangleHeight(self, elementNo, height, coorSys):
        self.sendMessage({'call' : 'set_rectangle_height',
                          'elementNo' : str(elementNo),
                          'height' : str(height),
                          'coorSys' : str(coorSys)})
        
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
        return float(width["width"])
    
    def relocateTexRectangle(self, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'set_texrectangle_top_left',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
        
    def shiftTexRectangle(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_texrectangle',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
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
    
    def setTexRectangleWidth(self, elementNo, width, coorSys):
        self.sendMessage({'call' : 'set_texrectangle_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width),
                          'coorSys' : str(coorSys)})
        
    def getTexRectangleWidth(self, elementNo):
        width = self.sendMessage({'call' : 'get_texrectangle_width',
                                  'elementNo' : str(elementNo)})
        return float(width["width"])
        
    def setTexRectangleHeight(self, elementNo, height, coorSys):
        self.sendMessage({'call' : 'set_texrectangle_height',
                          'elementNo' : str(elementNo),
                          'height' : str(height),
                          'coorSys' : str(coorSys)})
        
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
    
    def relocateText(self, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage({'call' : 'relocate_text',
                          'elementNo' : elementNo,
                          'x' : x, 
                          'y' : y, 
                          'coorSys' : coorSys,
                          'canvasNo' : canvasNo})
        
    def shiftText(self, elementNo, xDist, yDist, coorSys):
        self.sendMessage({'call' : 'shift_text',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def getTextPosition(self, elementNo):
        loc = self.sendMessage({'call' : 'get_text_pos',
                                'elementNo' : str(elementNo)})
        return [float(loc["x"]),float(loc["y"])]
    
    def getTextWidth(self, text, font, pointSize):
        width = self.sendMessage({'call' : 'get_text_width',
                          'text' : str(text),
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(width['width'])
    
    def getTextHeight(self, text, font, pointSize):
        height = self.sendMessage({'call' : 'get_text_height',
                          'text' : str(text),
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(height['height'])
    
    def getTextLineHeight(self, font, pointSize):
        height = self.sendMessage({'call' : 'get_text_line_height',
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(height['height'])
    
    def getTextDescenderHeight(self, font, pointSize):
        height = self.sendMessage({'call' : 'get_text_descender_height',
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(height['height'])
        
    def setPointSize(self, elementNo, pointSize):
        self.sendMessage({'call' : 'set_text_point_size',
                          'elementNo' : str(elementNo),
                          'pt' : str(pointSize)})
        
    def getPointSize(self, elementNo):
        size = self.sendMessage({'call' : 'get_text_point_size',
                                 'elementNo' : str(elementNo)})
        return int(size["size"])
    
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
        return bool(visibility["visible"])
        
    def hideSetupSurface(self):
        self.sendMessage({'call' : 'hide_setup_surface'})
        
    def showSetupSurface(self):
        self.sendMessage({'call' : 'show_setup_surface'})
        
    def getSetupSurfaceVisibility(self):
        return bool(self.sendMessage({'call' : 'get_setup_surface_visibility'}))
        
    def getClickedElements(self, surfaceNo, x, y):
        elements = self.sendMessage({'call' : 'get_clicked_elements',
                                     'surfaceNo' : str(surfaceNo),
                                     'x' : str(x),
                                     'y' : str(y)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
    
    def removeElement(self, elementNo, canvasNo):
        self.sendMessage({'call' : 'remove_element',
                          'elementNo' : str(elementNo),
                          'canvasNo' : str(canvasNo)})