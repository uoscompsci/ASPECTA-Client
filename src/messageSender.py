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
    dualProjector = True
    
    def encode_length(self, l):
        l = str(l)
        while len(l) < 8:
            l = "0" + l
        return l

    def uploadImage(self, fileParam):
        filename = fileParam.split("/")
        filename = filename[-1]
        self.sendMessage(1, {'call' : 'set_upload_name', 'filename' : filename})
        self.sendMessage(2, {'call' : 'set_upload_name', 'filename' : filename})
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
        
    def sendMessage(self, projector, message):
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
        self.sendMessage(1, {'call' : 'quit'})
        if self.dualProjector:
            self.sendMessage(2, {'call' : 'quit'})
        self.loop=False
        
    def quitClientOnly(self):
        self.loop=False
        
    def login(self, username):
        self.sendMessage(1, {'call' : 'login',
                          'username' : str(username)})
        if self.dualProjector:
            self.sendMessage(2, {'call' : 'login',
                              'username' : str(username)})
        
    def setapp(self, appname):
        self.sendMessage(1, {'call' : 'setapp',
                          'appname' : str(appname)})
        if self.dualProjector:
            self.sendMessage(2, {'call' : 'setapp',
                        'appname' : str(appname)})
    
    def newSurface(self, projector):
        sur = self.sendMessage(projector, {'call' : 'new_surface'})
        surNo = int(sur["surfaceNo"])
        return surNo
        
    def newSurfaceWithID(self, projector, ID):
        return self.sendMessage(projector, {'call' : 'new_surface_with_ID',
                                 'ID' : str(ID)})
    
    def newCursor(self, projector, surfaceNo, x, y, coorSys):
        cur = self.sendMessage(projector, {'call' : 'new_cursor',
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' : str(y),
                                'coorSys' : coorSys})
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newCursorWithID(self, projector, ID, surfaceNo, x, y, coorSys):
        cur = self.sendMessage(projector, {'call' : 'new_cursor_with_ID',
                                'ID' : str(ID), 
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' : str(y),
                                'coorSys' : coorSys})
        curNo = int(cur["cursorNo"])
        return curNo
    
    def newCanvas(self, projector, surfaceNo, x, y, width, height, coorSys, name):
        win = self.sendMessage(projector, {'call' : 'new_canvas',
                                'surfaceNo' : str(surfaceNo), 
                                'x' : str(x), 
                                'y' :  str(y), 
                                'width' : str(width), 
                                'height' : str(height),
                                'coorSys' : coorSys,
                                'name' : name})
        winNo = int(win["canvasNo"])
        return winNo
    
    def newCanvasWithID(self, projector, ID, surfaceNo, x, y, width, height, coorSys, name):
        win = self.sendMessage(projector, {'call' : 'new_canvas_with_ID',
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
    
    def newCircle(self, projector, canvasNo, x, y, radius, coorSys, lineCol, lineWidth, fillCol, sides):
        ele = self.sendMessage(projector, {'call' : 'new_circle',
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
    
    def newCircleWithID(self, projector, ID, canvasNo, x, y, radius, coorSys, lineCol, lineWidth, fillCol, sides):
        ele = self.sendMessage(projector, {'call' : 'new_circle_with_ID',
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
    
    def newLine(self, projector, canvasNo, xStart, yStart, xEnd, yEnd, coorSys, color, width):
        ele = self.sendMessage(projector, {'call' : 'new_line',
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
    
    def newLineWithID(self, projector, ID, canvasNo, xStart, yStart, xEnd, yEnd, coorSys, color, width):
        ele = self.sendMessage(projector, {'call' : 'new_line_with_ID',
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
    
    def newLineStrip(self, projector, canvasNo, x, y, coorSys, color, width):
        ele = self.sendMessage(projector, {'call' : 'new_line_strip',
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newLineStripWithID(self, projector, ID, canvasNo, x, y, coorSys, color, width):
        ele = self.sendMessage(projector, {'call' : 'new_line_strip_with_ID',
                                'ID' : str(ID), 
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'color' : self.colorString(color[0], color[1], color[2], color[3]),
                                'width' : str(width)})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newPolygon(self, projector, canvasNo, x, y, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage(projector, {'call' : 'new_polygon',
                                'canvasNo' : str(canvasNo),
                                'x' : str(x),
                                'y' : str(y),
                                'coorSys' : coorSys,
                                'lineColor' : self.colorString(lineColor[0], lineColor[1], lineColor[2], lineColor[3]),
                                'lineWidth' : str(lineWidth),
                                'fillColor' : self.colorString(fillColor[0], fillColor[1], fillColor[2], fillColor[3])})
        eleNo = int(ele["elementNo"])
        return eleNo
    
    def newPolygonWithID(self, projector, ID, canvasNo, x, y, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage(projector, {'call' : 'new_polygon_with_ID',
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
    
    def newTexRectangle(self, projector, canvasNo, x, y, width, height, coorSys, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ele = self.sendMessage(projector, {'call' : 'new_texrectangle',
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
    
    def newTexRectangleWithID(self, projector, ID, canvasNo, x, y, width, height, coorSys, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ele = self.sendMessage(projector, {'call' : 'new_texrectangle_with_ID',
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
    
    def newRectangle(self, projector, canvasNo, x, y, width, height, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage(projector, {'call' : 'new_rectangle',
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
    
    def newRectangleWithID(self, projector, ID, canvasNo, x, y, width, height, coorSys, lineColor, lineWidth, fillColor):
        ele = self.sendMessage(projector, {'call' : 'new_rectangle_with_ID',
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
    
    def newText(self, projector, canvasNo, text, x, y, coorSys, ptSize, font, color):
        ele = self.sendMessage(projector, {'call' : 'new_text',
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
    
    def newTextWithID(self, projector, ID, canvasNo, text, x, y, coorSys, ptSize, font, color):
        ele = self.sendMessage(projector, {'call' : 'new_text_with_ID',
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
    
    def subscribeToSurface(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'subscribe_to_surface',
                          'surfaceNo' : str(surfaceNo)})
    
    def getSurfaceID(self, projector, surfaceNo):
        ID = self.sendMessage(projector, {'call' : 'get_surface_ID',
                               'surfaceNo' : str(surfaceNo)})
        return ID["ID"]
    
    def setSurfaceID(self, projector, surfaceNo, ID):
        self.sendMessage(projector, {'call' : 'set_surface_ID',
                          'surfaceNo' : str(surfaceNo),
                          'ID' : str(ID)})
    
    def getSurfaceOwner(self, projector, surfaceNo):
        owner = self.sendMessage(projector, {'call' : 'get_surface_owner',
                                  'surfaceNo' : str(surfaceNo)})
        return owner["owner"]
        
    def getSurfaceAppDetails(self, projector, surfaceNo):
        details = self.sendMessage(projector, {'call' : 'get_surface_app_details',
                                    'surfaceNo' : str(surfaceNo)})
        return (details["app"],details["instance"])
        
    def getSurfacesByID(self, projector, ID):
        surfaces = self.sendMessage(projector, {'call' : 'get_surfaces_by_ID',
                                    'ID' : str(ID)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByOwner(self, projector, owner):
        surfaces = self.sendMessage(projector, {'call' : 'get_surfaces_by_owner',
                                     'owner' : str(owner)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByAppName(self, projector, name):
        surfaces = self.sendMessage(projector, {'call' : 'get_surfaces_by_app_name',
                                     'name' : str(name)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def getSurfacesByAppDetails(self, projector, name, instance):
        surfaces = self.sendMessage(projector, {'call' : 'get_surfaces_by_app_details',
                                     'name' : str(name),
                                     'number' : str(instance)})
        surfacelist = []
        for x in range(0,int(surfaces["count"])):
            surfacelist.append(int(surfaces[x]))
        return surfacelist
        
    def becomeSurfaceAdmin(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'become_surface_admin',
                          'surfaceNo' : str(surfaceNo)})
        
    def stopBeingSurfaceAdmin(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'stop_being_surface_admin',
                          'surfaceNo' : str(surfaceNo)})
        
    def setSurfaceEdges(self, projector, surfaceNo, topPoints, bottomPoints, leftPoints, rightPoints):
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
        self.sendMessage(projector, {'call' : 'set_surface_edges',
                          'surfaceNo' : str(surfaceNo),
                          'topString' : topString,
                          'bottomString' : bottomString,
                          'leftString' : leftString,
                          'rightString' : rightString})
        
    def undefineSurface(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'undefine_surface',
                          'surfaceNo' : str(surfaceNo)})
        
    def saveDefinedSurfaces(self, projector, filename):
        self.sendMessage(projector, {'call' : 'save_defined_surfaces',
                          'fileName' : str(filename)})
        
    def loadDefinedSurfaces(self, projector, filename):
        count = self.sendMessage(projector, {'call' : 'load_defined_surfaces',
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
        
    def getSavedLayouts(self, projector):
        layouts = self.sendMessage(projector, {'call' : 'get_saved_layouts'})
        layoutlist = []
        for x in range(0,int(layouts['count'])):
            layoutlist.append(layouts[str(x)])
        return layoutlist
    
    def getSavedImages(self, projector):
        images = self.sendMessage(projector, {'call' : 'get_saved_images'})
        imagelist = []
        for x in range(0,int(images['count'])):
            imagelist.append(images[str(x)])
        return imagelist
    
    def setSurfacePixelHeight(self, projector, surfaceNo, height):
        self.sendMessage(projector, {'call' : 'set_surface_pixel_height',
                          'surfaceNo' : str(surfaceNo),
                          'height' : str(height)})
        
    def setSurfacePixelWidth(self, projector, surfaceNo, width):
        self.sendMessage(projector, {'call' : 'set_surface_pixel_width',
                          'surfaceNo' : str(surfaceNo),
                          'width' : str(width)})
        
    def getSurfacePixelHeight(self, projector, surfaceNo):
        height = self.sendMessage(projector, {'call' : 'get_surface_pixel_height',
                                   'surfaceNo' : str(surfaceNo)})
        return height["height"]
        
    def getSurfacePixelWidth(self, projector, surfaceNo):
        width = self.sendMessage(projector, {'call' : 'get_surface_pixel_width',
                                  'surfaceNo' : str(surfaceNo)})
        return width["width"]
    
    def setSurfaceRealHeight(self, projector, surfaceNo, height):
        self.sendMessage(projector, {'call' : 'set_surface_real_height',
                          'surfaceNo' : str(surfaceNo),
                          'height' : str(height)})
        
    def setSurfaceRealWidth(self, projector, surfaceNo, width):
        self.sendMessage(projector, {'call' : 'set_surface_real_width',
                          'surfaceNo' : str(surfaceNo),
                          'width' : str(width)})
        
    def getSurfaceRealHeight(self, projector, surfaceNo):
        height = self.sendMessage(projector, {'call' : 'get_surface_real_height',
                                   'surfaceNo' : str(surfaceNo)})
        return height["height"]
        
    def getSurfaceRealWidth(self, projector, surfaceNo):
        width = self.sendMessage(projector, {'call' : 'get_surface_real_width',
                                  'surfaceNo' : str(surfaceNo)})
        return width["width"]
    
    def clearSurface(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'clear_surface',
                          'surfaceNo' : str(surfaceNo)})
    
    def deleteLayout(self, projector, name):
        self.sendMessage(projector, {'call' : 'delete_layout',
                          'name' : name})
        
    def deleteImage(self, projector, filename):
        self.sendMessage(projector, {'call' : 'delete_image',
                          'filename' : filename})
        
    def rotateSurfaceTo0(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'rotate_surface_to_0',
                          'surfaceNo' : str(surfaceNo)})
    
    def rotateSurfaceTo90(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'rotate_surface_to_90',
                          'surfaceNo' : str(surfaceNo)})
    
    def rotateSurfaceTo180(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'rotate_surface_to_180',
                          'surfaceNo' : str(surfaceNo)})
    
    def rotateSurfaceTo270(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'rotate_surface_to_270',
                          'surfaceNo' : str(surfaceNo)})
    
    def mirrorSurface(self, projector, surfaceNo):
        self.sendMessage(projector, {'call' : 'mirror_surface',
                          'surfaceNo' : str(surfaceNo)})
        
    def connectSurfaces(self, projector, surfaceNo1, side1, surfaceNo2, side2):
        self.sendMessage(projector, {'call' : 'connect_surfaces',
                          'surfaceNo1' : str(surfaceNo1),
                          'side1' : side1,
                          'surfaceNo2' : str(surfaceNo2),
                          'side2' : side2})
    
    def disconnectSurfaces(self, projector, surfaceNo1, side1, surfaceNo2, side2):
        self.sendMessage(projector, {'call' : 'disconnect_surfaces',
                          'surfaceNo1' : str(surfaceNo1),
                          'side1' : side1,
                          'surfaceNo2' : str(surfaceNo2),
                          'side2' : side2})
        
    def subscribeToCanvas(self, projector, canvasNo):
        self.sendMessage(projector, {'call' : 'subscribe_to_canvas',
                          'canvasNo' : str(canvasNo)})
        
    def getCanvasID(self, projector, canvasNo):
        ID = self.sendMessage(projector, {'call' : 'get_canvas_ID',
                               'canvasNo' : str(canvasNo)})
        return ID["ID"]
    
    def setCanvasID(self, projector, canvasNo, ID):
        self.sendMessage(projector, {'call' : 'set_canvas_ID',
                          'canvasNo' : str(canvasNo),
                          'ID' : str(ID)})
    
    def getCanvasOwner(self, projector, canvasNo):
        owner = self.sendMessage(projector, {'call' : 'get_canvas_owner',
                                  'canvasNo' : str(canvasNo)})
        return owner["owner"]
        
    def getCanvasAppDetails(self, projector, canvasNo):
        details = self.sendMessage(projector, {'call' : 'get_canvas_app_details',
                                    'canvasNo' : str(canvasNo)})
        return (details["app"],details["instance"])
        
    def getCanvasesByID(self, projector, ID):
        canvases = self.sendMessage(projector, {'call' : 'get_canvases_by_ID',
                                    'ID' : str(ID)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def getCanvasesByOwner(self, projector, owner):
        canvases = self.sendMessage(projector, {'call' : 'get_canvases_by_owner',
                                    'owner' : str(owner)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def getCanvasesByAppName(self, projector, name):
        canvases = self.sendMessage(projector, {'call' : 'get_canvases_by_app_name',
                                    'name' : str(name)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def getCanvasesByAppDetails(self, projector, name, instance):
        canvases = self.sendMessage(projector, {'call' : 'get_canvases_by_app_details',
                                    'name' : str(name),
                                    'number' : str(instance)})
        canvaslist = []
        for x in range(0,int(canvases["count"])):
            canvaslist.append(int(canvases[x]))
        return canvaslist
        
    def becomeCanvasAdmin(self, projector, canvasNo):
        self.sendMessage(projector, {'call' : 'become_canvas_admin',
                          'canvasNo' : str(canvasNo)})
        
    def stopBeingCanvasAdmin(self, projector, canvasNo):
        self.sendMessage(projector, {'call' : 'stop_being_canvas_admin',
                          'canvasNo' : str(canvasNo)})
        
    def subscribeToElement(self, projector, elementNo):
        self.sendMessage(projector, {'call' : 'subscribe_to_element',
                          'elementNo' : str(elementNo)})
        
    def getElementID(self, projector, elementNo):
        ID = self.sendMessage(projector, {'call' : 'get_element_ID',
                               'elementNo' : str(elementNo)})
        return ID["ID"]
    
    def setElementID(self, projector, elementNo, ID):
        self.sendMessage(projector, {'call' : 'set_element_ID',
                          'elementNo' : str(elementNo),
                          'ID' : str(ID)})
    
    def getElementOwner(self, projector, elementNo):
        owner = self.sendMessage(projector, {'call' : 'get_element_owner',
                                  'elementNo' : str(elementNo)})
        return owner["owner"]
        
    def getElementAppDetails(self, projector, surfaceNo):
        details = self.sendMessage(projector, {'call' : 'get_element_app_details',
                                    'surfaceNo' : str(surfaceNo)})
        return (details["app"],details["instance"])
        
    def getElementsByID(self, projector, ID):
        elements = self.sendMessage(projector, {'call' : 'get_elements_by_ID',
                                     'ID' : str(ID)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByOwner(self, projector, owner):
        elements = self.sendMessage(projector, {'call' : 'get_elements_by_owner',
                                     'owner' : str(owner)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByAppName(self, projector, name):
        elements = self.sendMessage(projector, {'call' : 'get_elements_by_app_name',
                                     'name' : str(name)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def getElementsByAppDetails(self, projector, name, instance):
        elements = self.sendMessage(projector, {'call' : 'get_elements_by_app_details',
                                     'name' : str(name),
                                     'number' : str(instance)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
    
    def getElementsOnCanvas(self, projector, canvasNo):
        elements = self.sendMessage(projector, {'call' : 'get_elements_on_canvas',
                                     'canvasNo' : str(canvasNo)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
        
    def becomeElementAdmin(self, projector, elementNo):
        self.sendMessage(projector, {'call' : 'become_element_admin',
                         'elementNo' : str(elementNo)})
        
    def stopBeingElementAdmin(self, projector, elementNo):
        self.sendMessage(projector, {'call' : 'stop_being_element_admin',
                          'elementNo' : str(elementNo)})
    
    def shiftCursor(self, projector, cursorNo, xDistance, yDistance):
        self.sendMessage(projector, {'call' : 'move_cursor',
                          'cursorNo' : str(cursorNo),
                          'xDist' : str(xDistance),
                          'yDist' : str(yDistance)})
        
    def testShiftCursor(self, projector, cursorNo, xDistance, yDistance):
        loc = self.sendMessage(projector, {'call' : 'test_move_cursor',
                                'cursorNo' : str(cursorNo),
                                'xDist' : str(xDistance),
                                'yDist' : str(yDistance)})
        return [loc["x"],loc["y"]]
    
    def relocateCursor(self, projector, cursorNo, x, y, coorSys, surfaceNo):
        self.sendMessage(projector, {'call' : 'relocate_cursor',
                          'cursorNo' : str(cursorNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'surfaceNo' : str(surfaceNo)})
    
    def getCursorPosition(self, projector, cursorNo):
        loc = self.sendMessage(projector, {'call' : 'get_cursor_pos',
                                'cursorNo' : str(cursorNo)})
        return [loc["x"],loc["y"]]
    
    def rotateCursorClockwise(self, projector, cursorNo, degrees):
        self.sendMessage(projector, {'call' : 'rotate_cursor_clockwise',
                          'cursorNo' : str(cursorNo),
                          'degrees' : str(degrees)})

    def rotateCursorAnticlockwise(self, projector, cursorNo, degrees):
        self.sendMessage(projector, {'call' : 'rotate_cursor_anticlockwise',
                          'cursorNo' : str(cursorNo),
                          'degrees' : str(degrees)})
    
    def getCursorRotation(self, projector, cursorNo):
        rotation = self.sendMessage(projector, {'call' : 'get_cursor_rotation',
                                     'cursorNo' : str(cursorNo)})
        return rotation["rotation"]
    
    def getCursorMode(self, projector, cursorNo):
        mode = self.sendMessage(projector, {'call' : 'get_cursor_mode',
                                 'cursorNo' : str(cursorNo)})
        return mode["mode"]
    
    def setCursorDefaultMode(self, projector, cursorNo):
        self.sendMessage(projector, {'call' : 'set_cursor_default_mode',
                          'cursorNo' : str(cursorNo)})
        
    def setCursorWallMode(self, projector, cursorNo):
        self.sendMessage(projector, {'call' : 'set_cursor_wall_mode',
                          'cursorNo' : str(cursorNo)})
        
    def setCursorBlockMode(self, projector, cursorNo):
        self.sendMessage(projector, {'call' : 'set_cursor_block_mode',
                          'cursorNo' : str(cursorNo)})
        
    def setCursorScreenMode(self, projector, cursorNo):
        self.sendMessage(projector, {'call' : 'set_cursor_screen_mode',
                          'cursorNo' : str(cursorNo)})
        
    def showCursor(self, projector, cursorNo):
        self.sendMessage(projector, {'call' : 'show_cursor',
                          'cursorNo' : str(cursorNo)})
    
    def hideCursor(self, projector, cursorNo):
        self.sendMessage(projector, {'call' : 'hide_cursor',
                          'cursorNo' : str(cursorNo)})

    def getCursorsSurface(self, projector, cursorNo):
        surfaceNo = self.sendMessage(projector, {'call' : 'get_cursors_surface',
                                      'cursorNo' : str(cursorNo)})
        return surfaceNo["surfaceNo"]
    
    def isCursorVisible(self, projector, cursorNo):
        visibility = self.sendMessage(projector, {'call' : 'isCursorVisible',
                                       'cursorNo' : str(cursorNo)})
        return visibility["visibility"]
    
    def shiftCanvas(self, projector, canvasNo, xDistance, yDistance, coorSys):
        self.sendMessage(projector, {'call' : 'move_canvas',
                          'canvasNo' : str(canvasNo),
                          'xDist' : str(xDistance),
                          'yDist' : str(yDistance),
                          'coorSys' : str(coorSys)})
        
    def relocateCanvas(self, projector, canvasNo, x, y, coorSys, surfaceNo):
        self.sendMessage(projector, {'call' : 'relocate_canvas',
                          'canvasNo' : str(canvasNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'surfaceNo' : str(surfaceNo)})
        
    def setCanvasWidth(self, projector, canvasNo, width, coorSys):
        self.sendMessage(projector, {'call' : 'set_canvas_width',
                          'canvasNo' : str(canvasNo),
                          'width' : str(width),
                          'coorSys' : str(coorSys)})
        
    def setCanvasHeight(self, projector, canvasNo, height, coorSys):
        self.sendMessage(projector, {'call' : 'set_canvas_height',
                          'canvasNo' : str(canvasNo),
                          'height' : str(height),
                          'coorSys' : str(coorSys)})
        
    def getCanvasPosition(self, projector, canvasNo):
        loc = self.sendMessage(projector, {'call' : 'get_canvas_pos',
                                'canvasNo' : str(canvasNo)})
        return [loc["x"],loc["y"]]
        
    def getCanvasWidth(self, projector, canvasNo):
        width = self.sendMessage(projector, {'call' : 'get_canvas_width',
                                  'canvasNo' : str(canvasNo)})
        return width["width"]
        
    def getCanvasHeight(self, projector, canvasNo):
        height = self.sendMessage(projector, {'call' : 'get_canvas_height',
                                   'canvasNo' : str(canvasNo)})
        return height["height"]
        
    def stretchCanvasDown(self, projector, canvasNo, distance, coorSys):
        self.sendMessage(projector, {'call' : 'stretch_canvas_down',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def stretchCanvasUp(self, projector, canvasNo, distance, coorSys):
        self.sendMessage(projector, {'call' : 'stretch_canvas_up',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def stretchCanvasLeft(self, projector, canvasNo, distance, coorSys):
        self.sendMessage(projector, {'call' : 'stretch_canvas_left',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def stretchCanvasRight(self, projector, canvasNo, distance, coorSys):
        self.sendMessage(projector, {'call' : 'stretch_canvas_right',
                          'canvasNo' : str(canvasNo),
                          'distance' : str(distance),
                          'coorSys' : str(coorSys)})
        
    def setCanvasName(self, projector, canvasNo, name):
        self.sendMessage(projector, {'call' : 'set_canvas_name',
                          'canvasNo' : str(canvasNo),
                          'name' : name})
        
    def getCanvasName(self, projector, canvasNo):
        name = self.sendMessage(projector, {'call' : 'get_canvas_name',
                                 'canvasNo' : str(canvasNo)})
        return name["name"]

    def getCanvasSurface(self, projector, canvasNo):
        surfaceNo = self.sendMessage(projector, {'call' : 'get_canvas_surface',
                                      'canvasNo' : str(canvasNo)})
        return surfaceNo["surfaceNo"]
    
    def shiftCircle(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_circle',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocateCircle(self, projector, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'relocate_circle',
                          'elementNo' : elementNo, 
                          'x' : x, 
                          'y' : y, 
                          'coorSys' : coorSys,
                          'canvasNo' : canvasNo})
        
    def getCirclePosition(self, projector, elementNo):
        loc = self.sendMessage(projector, {'call' : 'get_circle_pos',
                                    'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
    
    def getElementType(self, projector, elementNo):
        typeName = self.sendMessage(projector, {'call' : 'get_element_type',
                                 'elementNo' : str(elementNo)})
        return typeName["type"]

    def getElementsCanvas(self, projector, elementNo):
        canvasNo = self.sendMessage(projector, {'call' : 'get_elements_canvas',
                                     'elementNo' : str(elementNo)})
        return canvasNo["canvasNo"]
    
    def setCircleLineColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_circle_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setCircleLineWidth(self, projector, elementNo, width):
        self.sendMessage(projector, {'call' : 'set_circle_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def setCircleFillColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_circle_fill_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})

    def getCircleLineColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_circle_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def getCircleLineWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_circle_line_width',
                                 'elementNo' : str(elementNo)})
        return width["width"]
        
    def getCircleFillColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_circle_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setCircleRadius(self, projector, elementNo, radius, coorSys):
        self.sendMessage(projector, {'call' : 'set_circle_radius',
                          'elementNo' : str(elementNo),
                          'radius' : str(radius),
                          'coorSys' : str(coorSys)})
        
    def getCircleRadius(self, projector, elementNo):
        radius = self.sendMessage(projector, {'call' : 'get_circle_radius',
                                   'elementNo' : str(elementNo)})
        return radius["radius"]
    
    def setCircleSides(self, projector, elementNo, sides):
        self.sendMessage(projector, {'call' : 'set_circle_sides',
                          'elementNo' : str(elementNo),
                          'sides' : str(sides)})
        
    def getCircleSides(self, projector, elementNo):
        sides = self.sendMessage(projector, {'call' : 'get_circle_sides',
                                  'elementNo' : str(elementNo)})
        return sides["sides"]
    
    def shiftLine(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_line',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocateLine(self, projector, elementNo, refPoint, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'relocate_line',
                          'elementNo' : str(elementNo),
                          'refPoint' : str(refPoint),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
    
    def getLineStart(self, projector, elementNo):
        loc = self.sendMessage(projector, {'call' : 'get_line_start',
                                'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
    
    def getLineEnd(self, projector, elementNo):
        loc = self.sendMessage(projector, {'call' : 'get_line_end',
                                'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
    
    def setLineStart(self, projector, elementNo, x, y, coorSys):
        self.sendMessage(projector, {'call' : 'relocate_line_start',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
    
    def setLineEnd(self, projector, elementNo, x, y, coorSys):
        self.sendMessage(projector, {'call' : 'relocate_line_end',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
    
    def setLineColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getLineColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setLineWidth(self, projector, elementNo, width):
        self.sendMessage(projector, {'call' : 'set_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getLineWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_line_width',
                                  'elementNo' : str(elementNo)})
        return width["width"]
    
    def addLineStripPoint(self, projector, elementNo, x, y, coorSys):
        self.sendMessage(projector, {'call' : 'add_line_strip_point',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : coorSys})
        
    def addLineStripPointAt(self, projector, elementNo, x, y, coorSys, index):
        self.sendMessage(projector, {'call' : 'add_line_strip_point_at',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : coorSys,
                          'index' : str(index)})
        
    def getLineStripPoint(self, projector, elementNo, pointNo):
        loc = self.sendMessage(projector, {'call' : 'get_line_strip_point',
                                'elementNo' : str(elementNo),
                                'index' : str(pointNo)})
        return [loc["x"],loc["y"]]
        
    def shiftLineStrip(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_line_strip',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocateLineStrip(self, projector, elementNo, refPoint, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'relocate_line_strip',
                          'elementNo' : str(elementNo),
                          'refPoint' : str(refPoint),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
    
    def moveLineStripPoint(self, projector, elementNo, pointNo, x, y, coorSys):
        self.sendMessage(projector, {'call' : 'relocate_line_strip_point',
                          'elementNo' : str(elementNo),
                          'pointNo' : str(pointNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : coorSys})
        
    def getLineStripColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_line_strip_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def setLineStripColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_line_strip_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setLineStripWidth(self, projector, elementNo, width):
        self.sendMessage(projector, {'call' : 'set_line_strip_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getLineStripWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_line_strip_width',
                                  'elementNo' : str(elementNo)})
        return width["width"]
        
    def getLineStripPointCount(self, projector, elementNo):
        count = self.sendMessage(projector, {'call' : 'get_line_strip_point_count',
                                  'elementNo' : str(elementNo)})
        return count["count"]
    
    def setLineStripContent(self, projector, elementNo, content):
        converted = str(content[0][0]) + ":" + str(content[0][1])
        for y in range(0,len(content)):
            converted += ";" + str(content[y][0]) + ":" + str(content[y][1])
        self.sendMessage(projector, {'call' : 'set_line_strip_content',
                          'elementNo' : str(elementNo), 
                          'content' : converted})
    
    def addPolygonPoint(self, projector, elementNo, x, y, coorSys):
        self.sendMessage(projector, {'call' : 'add_polygon_point',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
        
    def getPolygonPoint(self, projector, elementNo, pointNo):
        loc = self.sendMessage(projector, {'call' : 'get_polygon_point',
                                'elementNo' : str(elementNo),
                                'index' : str(pointNo)})
        return (loc["x"],loc["y"])
    
    def shiftPolygon(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_polygon',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def relocatePolygon(self, projector, elementNo, refPoint, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'relocate_polygon',
                          'elementNo' : str(elementNo),
                          'refPoint' : str(refPoint),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
    
    def movePolygonPoint(self, projector, elementNo, pointNo, x, y, coorSys):
        self.sendMessage(projector, {'call' : 'relocate_polygon_point',
                          'elementNo' : str(elementNo),
                          'index' : str(pointNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys)})
        
    def getPolygonFillColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_polygon_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setPolygonFillColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_polygon_fill_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getPolygonLineColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_polygon_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def getPolygonLineWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_polygon_line_width',
                                 'elementNo' : str(elementNo)})
        return width["width"]
    
    def setPolygonLineColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_polygon_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setPolygonLineWidth(self, projector, elementNo, width):
        self.sendMessage(projector, {'call' : 'set_polygon_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getPolygonPointCount(self, projector, elementNo):
        count = self.sendMessage(projector, {'call' : 'get_polygon_point_count',
                                  'elementNo' : str(elementNo)})
        return count["count"]
    
    def relocateRectangle(self, projector, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'set_rectangle_top_left',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
        
    def shiftRectangle(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_rectangle',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def getRectangleTopLeft(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_rectangle_top_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleTopRight(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_rectangle_top_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleBottomRight(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_rectangle_bottom_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getRectangleBottomLeft(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_rectangle_bottom_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def setRectangleWidth(self, projector, elementNo, width, coorSys):
        self.sendMessage(projector, {'call' : 'set_rectangle_width',
                         'elementNo' : str(elementNo),
                         'width' : str(width),
                         'coorSys' : str(coorSys)})
        
    def getRectangleWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_rectangle_width',
                                  'elementNo' : str(elementNo)})
        return float(width["width"])
        
    def setRectangleHeight(self, projector, elementNo, height, coorSys):
        self.sendMessage(projector, {'call' : 'set_rectangle_height',
                          'elementNo' : str(elementNo),
                          'height' : str(height),
                          'coorSys' : str(coorSys)})
        
    def getRectangleHeight(self, projector, elementNo):
        height = self.sendMessage(projector, {'call' : 'get_rectangle_height',
                                   'elementNo' : str(elementNo)})
        return float(height["height"])
    
    def setRectangleFillColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_rectangle_fill_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getRectangleFillColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_rectangle_fill_color',
                                                 'elementNo' : str(elementNo)})["color"])
    
    def setRectangleLineColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_rectangle_line_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def setRectangleLineWidth(self, projector, elementNo, width):
        self.sendMessage(projector, {'call' : 'set_rectangle_line_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width)})
        
    def getRectangleLineColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_rectangle_line_color',
                                                 'elementNo' : str(elementNo)})["color"])
        
    def getRectangleLineWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_rectangle_line_width',
                                 'elementNo' : str(elementNo)})
        return width["width"]
    
    def relocateTexRectangle(self, projector, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'set_texrectangle_top_left',
                          'elementNo' : str(elementNo),
                          'x' : str(x),
                          'y' : str(y),
                          'coorSys' : str(coorSys),
                          'canvasNo' : str(canvasNo)})
        
    def shiftTexRectangle(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_texrectangle',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def getTexRectangleTopLeft(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_texrectangle_top_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleTopRight(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_texrectangle_top_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleBottomRight(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_texrectangle_bottom_right',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleBottomLeft(self, projector, elementNo):
        pos = self.sendMessage(projector, {'call' : 'get_texrectangle_bottom_left',
                                'elementNo' : str(elementNo)})
        return (float(pos["x"]),float(pos["y"]))
    
    def getTexRectangleTexture(self, projector, elementNo):
        tex = self.sendMessage(projector, {'call' : 'get_texrectangle_texture',
                                'elementNo' : str(elementNo)})
        return tex["texture"]
    
    def setTexRectangleTexture(self, projector, elementNo, filename):
        extension = filename.split(".")[-1]
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            self.sendMessage(projector, {'call' : 'set_texrectangle_texture',
                              'elementNo' : str(elementNo),
                              'textureData' : encoded_string,
                              'extension' : extension})
    
    def setTexRectangleWidth(self, projector, elementNo, width, coorSys):
        self.sendMessage(projector, {'call' : 'set_texrectangle_width',
                          'elementNo' : str(elementNo),
                          'width' : str(width),
                          'coorSys' : str(coorSys)})
        
    def getTexRectangleWidth(self, projector, elementNo):
        width = self.sendMessage(projector, {'call' : 'get_texrectangle_width',
                                  'elementNo' : str(elementNo)})
        return float(width["width"])
        
    def setTexRectangleHeight(self, projector, elementNo, height, coorSys):
        self.sendMessage(projector, {'call' : 'set_texrectangle_height',
                          'elementNo' : str(elementNo),
                          'height' : str(height),
                          'coorSys' : str(coorSys)})
        
    def getTexRectangleHeight(self, projector, elementNo):
        height = self.sendMessage(projector, {'call' : 'get_texrectangle_height',
                                   'elementNo' : str(elementNo)})
        return float(height["height"])
    
    def setText(self, projector, elementNo, text):
        self.sendMessage(projector, {'call' : 'set_text',
                          'elementNo' : str(elementNo),
                          'text' : text})
        
    def getText(self, projector, elementNo):
        text = self.sendMessage(projector, {'call' : 'get_text',
                                 'elementNo' : str(elementNo)})
        return text["text"]
    
    def relocateText(self, projector, elementNo, x, y, coorSys, canvasNo):
        self.sendMessage(projector, {'call' : 'relocate_text',
                          'elementNo' : elementNo,
                          'x' : x, 
                          'y' : y, 
                          'coorSys' : coorSys,
                          'canvasNo' : canvasNo})
        
    def shiftText(self, projector, elementNo, xDist, yDist, coorSys):
        self.sendMessage(projector, {'call' : 'shift_text',
                          'elementNo' : str(elementNo),
                          'xDist' : str(xDist),
                          'yDist' : str(yDist),
                          'coorSys' : str(coorSys)})
        
    def getTextPosition(self, projector, elementNo):
        loc = self.sendMessage(projector, {'call' : 'get_text_pos',
                                'elementNo' : str(elementNo)})
        return [loc["x"],loc["y"]]
    
    def getTextWidth(self, projector, text, font, pointSize):
        width = self.sendMessage(projector, {'call' : 'get_text_width',
                          'text' : str(text),
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(width['width'])
    
    def getTextHeight(self, projector, text, font, pointSize):
        height = self.sendMessage(projector, {'call' : 'get_text_height',
                          'text' : str(text),
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(height['height'])
    
    def getTextLineHeight(self, projector, font, pointSize):
        height = self.sendMessage(projector, {'call' : 'get_text_line_height',
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(height['height'])
    
    def getTextDescenderHeight(self, projector, font, pointSize):
        height = self.sendMessage(projector, {'call' : 'get_text_descender_height',
                          'pt' : str(pointSize),
                          'font' : str(font)})
        return float(height['height'])
        
    def setPointSize(self, projector, elementNo, pointSize):
        self.sendMessage(projector, {'call' : 'set_text_point_size',
                          'elementNo' : str(elementNo),
                          'pt' : str(pointSize)})
        
    def getPointSize(self, projector, elementNo):
        size = self.sendMessage(projector, {'call' : 'get_text_point_size',
                                 'elementNo' : str(elementNo)})
        return size["size"]
    
    def getFont(self, projector, elementNo):
        font = self.sendMessage(projector, {'call' : 'get_text_font',
                                 'elementNo' : str(elementNo)})
        return font["font"]
    
    def setFont(self, projector, elementNo, font):
        self.sendMessage(projector, {'call' : 'set_text_font',
                          'elementNo' : str(elementNo),
                          'font' : font})
        
    def setTextColor(self, projector, elementNo, color):
        self.sendMessage(projector, {'call' : 'set_text_color',
                          'elementNo' : str(elementNo),
                          'color' : self.colorString(color[0], color[1], color[2], color[3])})
        
    def getTextColor(self, projector, elementNo):
        return self.colorTuple(self.sendMessage(projector, {'call' : 'get_text_color',
                                                 'elementNo' : str(elementNo)})["color"])
           
    def showElement(self, projector, elementNo):
        self.sendMessage(projector, {'call' : 'show_element',
                         'elementNo' : str(elementNo)})
        
    def hideElement(self, projector, elementNo):
        self.sendMessage(projector, {'call' : 'hide_element',
                          'elementNo' : str(elementNo)})
        
    def checkElementVisibility(self, projector, elementNo):
        visibility = self.sendMessage(projector, {'call' : 'check_element_visibility',
                                       'elementNo' : str(elementNo)})
        return visibility["visible"]
        
    def hideSetupSurface(self, projector):
        self.sendMessage(projector, {'call' : 'hide_setup_surface'})
        
    def showSetupSurface(self, projector):
        self.sendMessage(projector, {'call' : 'show_setup_surface'})
        
    def getSetupSurfaceVisibility(self, projector):
        return self.sendMessage(projector, {'call' : 'get_setup_surface_visibility'})
        
    def getClickedElements(self, projector, surfaceNo, x, y):
        elements = self.sendMessage(projector, {'call' : 'get_clicked_elements',
                                     'surfaceNo' : str(surfaceNo),
                                     'x' : str(x),
                                     'y' : str(y)})
        elementlist = []
        for x in range(0,int(elements["count"])):
            elementlist.append(int(elements[x]))
        return elementlist
    
    def removeElement(self, projector, elementNo, canvasNo):
        self.sendMessage(projector, {'call' : 'remove_element',
                          'elementNo' : str(elementNo),
                          'canvasNo' : str(canvasNo)})