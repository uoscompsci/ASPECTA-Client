from messageSender import *
import pygame
import threading
import time
from pygame.locals import *
from math import *
from bezier import *
from ConfigParser import SafeConfigParser

class point:
    __slots__ = ['x','y']
    
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
    def setX(self,x):
        self.x = x
        
    def setY(self,y):
        self.y = y
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y

class client:
    __slots__ = ['ppe', 'topbz', 'bottombz', 'leftbz', 'rightbz']
    quit = False
    topCircles = []
    bottomCircles = []
    leftCircles = []
    rightCircles = []
    topCP = []
    bottomCP = []
    leftCP = []
    rightCP = [] 
    dragging = []
    bezierUpdates = [False,False,False,False] #[top,bottom,left,right]
    refreshrate = 0
    
    def bezierUpdateTracker(self):
        while(True):
            if (self.bezierUpdates[0]==True):
                self.updateBezier("top")
                self.bezierUpdates[0] = False
            if (self.bezierUpdates[1]==True):
                self.updateBezier("bottom")
                self.bezierUpdates[1] = False
            if(self.bezierUpdates[2] == True):
                self.updateBezier("left")
                self.bezierUpdates[2] = False
            if(self.bezierUpdates[3] == True):
                self.updateBezier("right")
                self.bezierUpdates[3] = False
            time.sleep(self.refreshrate)
    
    def getMidPoints(self, point1, point2):
        return ((float(point1[0])+float(point2[0]))/float(2), (float(point1[1])+float(point2[1]))/float(2))
    
    def oppControl(self, point, control):
        return (float(point[0])+(float(point[0])-float(control[0])),float(point[1])+(float(point[1])-float(control[1])))
    
    def splitSide(self, circles, side):
        count = len(circles)
        insert = []
        for x in range(1, count):
            point1 = self.sender.getCirclePosition(circles[x-1])
            point2 = self.sender.getCirclePosition(circles[x])
            midpoint = self.getMidPoints((point1[0],point1[1]), (point2[0],point2[1])) 
            insert.append(midpoint)
        for x in reversed(range(0,len(insert))):
            ele = self.sender.newCircle(1, insert[x][0], int(insert[x][1]), 10, (1, 0, 0, 1), (0, 1, 0, 1), 20)
            circles.insert(x+1, ele)
        if(side == "top"):
            self.bezierUpdates[0] = True
        elif(side == "bottom"):
            self.bezierUpdates[1] = True
        elif(side == "left"):
            self.bezierUpdates[2] = True
        elif(side == "right"):
            self.bezierUpdates[3] = True
            
    def updateBezier(self, side):
        points = []
        circles = []
        if(side=="top"):
            circles = self.topCircles
        elif(side=="bottom"):
            circles = self.bottomCircles
        elif(side=="left"):
            circles = self.leftCircles
        elif(side=="right"):
            circles = self.rightCircles
        for x in range(0,len(circles)):
            pos = self.sender.getCirclePosition(circles[x])
            points.append((pos[0],pos[1]))
        calc = bezierCalc()
        if(side=="top"):
            curve = calc.getCurvePoints(points, self.ppe)
            self.sender.setLineStripContent(self.topbz,curve)
        elif(side=="bottom"):
            curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
            self.sender.setLineStripContent(self.bottombz,curve)
        elif(side=="left"):
            curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
            self.sender.setLineStripContent(self.leftbz,curve)
        elif(side=="right"):
            curve = calc.getCurvePoints(points, self.ppe)
            self.sender.setLineStripContent(self.rightbz,curve)
            
    def isHit(self, point1, point2):
        a = abs(float(point1[0])-float(point2[0]))
        b = abs(float(point1[1])-float(point2[1]))
        csq = pow(a,2) + pow(b,2)
        c = sqrt(csq)
        if (c<10):
            return True
        else:
            return False

    def getInput(self,get_point):
        #mpb=pygame.mouse.get_pressed() # mouse pressed buttons
        #kpb=pygame.key.get_pressed() # keyboard pressed buttons
        pos=pygame.mouse.get_pos() # mouse shift
        for event in pygame.event.get():
            if event.type == QUIT:
                    self.quit = True
                    return None
            elif event.type == pygame.KEYDOWN:
                if event.key==pygame.K_l:
                    if (self.mouseLock == True):
                        self.mouseLock = False
                        pygame.mouse.set_visible(True)
                    elif(self.mouseLock == False):
                        self.mouseLock = True
                        pygame.mouse.set_visible(False)
                elif event.key==pygame.K_UP:
                    self.splitSide(self.topCircles, "top")
                elif event.key==pygame.K_DOWN:
                    self.splitSide(self.bottomCircles, "bottom")
                elif event.key==pygame.K_LEFT:
                    self.splitSide(self.leftCircles, "left")
                elif event.key==pygame.K_RIGHT:
                    self.splitSide(self.rightCircles, "right")
                elif event.key==pygame.K_SPACE:
                    topPoints = []
                    for x in range(0,len(self.topCircles)):
                        topPoints.append(self.sender.getCirclePosition(self.topCircles[x]))
                    bottomPoints = []
                    for x in range(0,len(self.bottomCircles)):
                        bottomPoints.append(self.sender.getCirclePosition(self.bottomCircles[len(self.bottomCircles) - 1 - x]))
                    leftPoints = []
                    for x in range(0,len(self.leftCircles)):
                        leftPoints.append(self.sender.getCirclePosition(self.leftCircles[x]))
                    rightPoints = []
                    for x in range(0,len(self.rightCircles)):
                        rightPoints.append(self.sender.getCirclePosition(self.rightCircles[len(self.rightCircles) - 1 - x]))
                    #print "left = " + str(leftPoints)
                    #print "right = " + str(rightPoints)
                    self.sender.setSurfaceEdges(self.warpedSurf, topPoints, bottomPoints, leftPoints, rightPoints)
                elif event.key==pygame.K_ESCAPE:
                    self.sender.quit()
            if(self.mouseLock==True):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==4:
                        self.sender.rotateCursorClockwise(1,10)
                    elif event.button==5:
                        self.sender.rotateCursorAnticlockwise(1,10)
                    elif event.button==1:
                        if(get_point==True):
                            loc = self.sender.getCursorPosition(1)
                            ele = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 0, 0, 1), 20)
                            return (loc, ele)
                        if(get_point!=True):
                            loc = self.sender.getCursorPosition(1)
                            self.dragging = []
                            for x in range(0,len(self.topCircles)):
                                point = self.sender.getCirclePosition(self.topCircles[x])
                                if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                    self.dragging.append(self.topCircles[x])
                            for x in range(0,len(self.bottomCircles)):
                                point = self.sender.getCirclePosition(self.bottomCircles[x])
                                if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                    self.dragging.append(self.bottomCircles[x])
                            for x in range(0,len(self.leftCircles)):
                                point = self.sender.getCirclePosition(self.leftCircles[x])
                                if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                    self.dragging.append(self.leftCircles[x])
                            for x in range(0,len(self.rightCircles)):
                                point = self.sender.getCirclePosition(self.rightCircles[x])
                                if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                    self.dragging.append(self.rightCircles[x])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if (event.button==1 and len(self.topCircles)>1 and len(self.bottomCircles)>1 and len(self.leftCircles)>1 and len(self.rightCircles)>1):
                        self.dragging=[]
                        topPoints = []
                        for x in range(0,len(self.topCircles)):
                            topPoints.append(self.sender.getCirclePosition(self.topCircles[x]))
                        bottomPoints = []
                        for x in range(0,len(self.bottomCircles)):
                            bottomPoints.append(self.sender.getCirclePosition(self.bottomCircles[len(self.bottomCircles) - 1 - x]))
                        leftPoints = []
                        for x in range(0,len(self.leftCircles)):
                            leftPoints.append(self.sender.getCirclePosition(self.leftCircles[x]))
                        rightPoints = []
                        for x in range(0,len(self.rightCircles)):
                            rightPoints.append(self.sender.getCirclePosition(self.rightCircles[len(self.rightCircles) - 1 - x]))
                        #print "left = " + str(leftPoints)
                        #print "right = " + str(rightPoints)
                        self.sender.setSurfaceEdges(self.warpedSurf, topPoints, bottomPoints, leftPoints, rightPoints)
                        
                        
                xdist = (self.winWidth/2)-pos[0]
                ydist = (self.winHeight/2)-pos[1]
                pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                
                loc = self.sender.testMoveCursor(1,-xdist,ydist)

                if (loc[0]<0):
                    loc[0]=0
                elif(loc[0]>1280):
                    loc[0]=1280
                if(loc[1]<0):
                    loc[1] = 0
                elif(loc[1]>1024):
                    loc[1] = 1024
                self.sender.relocateCursor(1,float(loc[0]),float(loc[1]),0)
                if(len(self.dragging)!=0):
                    for x in range (0,len(self.dragging)):
                        self.sender.relocateCircle(self.dragging[x], float(loc[0]), float(loc[1]), 1)
                        if(self.topCircles.__contains__(self.dragging[x])):
                            self.bezierUpdates[0] = True
                        if(self.bottomCircles.__contains__(self.dragging[x])):
                            self.bezierUpdates[1] = True
                        if(self.leftCircles.__contains__(self.dragging[x])):
                            self.bezierUpdates[2] = True
                        if(self.rightCircles.__contains__(self.dragging[x])):
                            self.bezierUpdates[3] = True
        return None
    
    def __init__(self):
        parser = SafeConfigParser()
        parser.read("config.ini")
        self.ppe = parser.getint('RoomSetup','PointsPerEdge')
        self.refreshrate = 1/(parser.getint('library','MovesPerSecond'))
        self.mouseLock = False
        self.sender = messageSender()
        self.winWidth = 320
        self.winHeight = 240
        
        # Initialise screen
        pygame.init()
        screen = pygame.display.set_mode((self.winWidth, self.winHeight))
        pygame.display.set_caption('Room setup program')
    
        # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((255, 255, 255))
    
        # Display some text
        font = pygame.font.Font(None, 36)

        # Blit everything to the screen
        screen.blit(background, (0, 0))
        pygame.display.flip()
        
        self.sender.login("jp438")
        self.sender.setapp("myapp")
        self.sender.showSetupSurface()
        self.warpedSurf = self.sender.newSurface()
        self.sender.newWindow(0, 0, 1024, 1280, 1024, "setupWindow")
        self.sender.newCursor(0, 1280/2, 1024/2)
        
        window = self.sender.newWindow(self.warpedSurf, 200, 200, 100, 100, "Bob")
        self.sender.newCursor(self.warpedSurf, 512/2, 512/2)
        self.sender.newTexRectangle(window, 200, 400, 300, 400, "Mona_Lisa.jpg")
        self.sender.newRectangle(window, 50, 400, 100, 200, (1,1,1,1), (0.5,0.3,0.5,1))
        self.sender.newCircle(window, 50, 50, 50, (1,1,1,1), (1,0,1,1), 50)
        self.sender.newCircle(window, 250, 100, 50, (1,1,1,1), (0,1,0,1), 50)
        self.sender.newCircle(window, 415, 250, 50, (1,1,1,1), (1,1,0,1), 50)
        self.sender.newCircle(window, 200, 200, 50, (1,1,1,1), (1,0,0,1), 50)
        self.blueCirc = self.sender.newCircle(window, 400, 300, 50, (1,1,1,1), (0,0,1,1), 50)
        self.sender.newCircle(window, 300, 512, 50, (1,1,1,1), (0.5,0.5,0.5,1), 50)
        
        #self.sender.newRectangle(window, 200, 200, 100, 200, (1,1,1,1), (0,0,1,1))

        self.mouseLock=True
        pygame.mouse.set_visible(False)
        
        self.sender.newText(window, "Hello World  | dlroW olleH", 100, 100, 30, "Arial", (1,1,0,1))
        self.sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
        self.sender.newText(window, "Hello World  | dlroW olleH", 100, 200, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Hello World  | dlroW olleH", 100, 300, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Hello World  | dlroW olleH", 100, 400, 30, "Arial", (1,1,0,1))
        
        ele = self.sender.newPolygon(window, 100, 100, (1,1,1,1), (0.5,0.5,0.5,1))
        self.sender.addPolygonPoint(ele, 200, 150)
        self.sender.addPolygonPoint(ele, 200, 200)
        self.sender.addPolygonPoint(ele, 150, 175)
        self.sender.addPolygonPoint(ele, 75, 175)
        self.sender.addPolygonPoint(ele, 50, 150)
        #self.sender.addPolygonPoint(ele, 200, 150)
        #self.sender.addPolygonPoint(ele, 200, 150)
        tl = None
        bl = None
        tr = None
        br = None
        
        while(self.quit==False and tl==None):
            background.fill((255, 255, 255))
            text = font.render("Click the top left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            tl = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.topCircles.append(tl[1])
        self.topbz = self.sender.newLineStrip(1, tl[0][0], tl[0][1], (1,1,1,1), 5)
        
            
        while(self.quit==False and tr==None):
            background.fill((255, 255, 255))
            text = font.render("Click the top right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            tr = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.topCircles.append(tr[1])
        self.sender.addLineStripPoint(self.topbz, tr[0][0], tr[0][1])
        self.rightCircles.append(tr[1])
        self.rightbz = self.sender.newLineStrip(1, tr[0][0], tr[0][1], (1,1,1,1), 5)
            
        while(self.quit==False and br==None):
            background.fill((255, 255, 255))
            text =font.render("Click the bottom right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            br = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.rightCircles.append(br[1])
        self.sender.addLineStripPoint(self.rightbz, br[0][0], br[0][1])
        self.bottomCircles.append(br[1])
        self.bottombz = self.sender.newLineStrip(1, br[0][0], br[0][1], (1,1,1,1), 5)
            
        while(self.quit==False and bl==None):
            background.fill((255, 255, 255))
            text = font.render("Click the bottom left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            bl = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.bottomCircles.append(bl[1])
        self.sender.addLineStripPoint(self.bottombz, bl[0][0], bl[0][1])
        self.leftCircles.append(bl[1])
        self.leftbz = self.sender.newLineStrip(1, bl[0][0], bl[0][1], (1,1,1,1), 5)
        self.leftCircles.append(tl[1])
        self.sender.addLineStripPoint(self.leftbz, tl[0][0], tl[0][1])
        
        thread = threading.Thread(target=self.bezierUpdateTracker, args=()) #Creates the display thread
        thread.start() #Starts the display thread
        dirleft = True
        while(self.quit==False):
            background.fill((255, 255, 255))
            text = font.render("Press 'L' to release mouse", 1, (10, 10, 10))
            pos = self.sender.getCirclePosition(self.blueCirc)
            if(pos[0]>=512):
                dirleft = False
            if(pos[0]<=0):
                dirleft = True
            if(dirleft):
                self.sender.relocateCircle(self.blueCirc, pos[0]+0.1, pos[1], window)
            else:
                self.sender.relocateCircle(self.blueCirc, pos[0]-0.1, pos[1], window)
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.getInput(False)
            screen.blit(background, (0, 0))
            pygame.display.flip()

client()