from messageSender import *
import pygame
import threading
import time
from pygame.locals import *
from math import *
from bezier import *
from ConfigParser import SafeConfigParser
import datetime

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
    __slots__ = ['ppe']
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
    warpedSurf = {}
    bezierUpdates = {} #[top,bottom,left,right]
    refreshrate = 0
    
    def bezierUpdateTracker(self):
        while(True):
            for x in range(0,len(self.bezierUpdates)):
                if (self.bezierUpdates[x][0]==True):
                    self.updateBezier("top",x)
                    self.bezierUpdates[x][0] = False
                if (self.bezierUpdates[x][1]==True):
                    self.updateBezier("bottom",x)
                    self.bezierUpdates[x][1] = False
                if(self.bezierUpdates[x][2] == True):
                    self.updateBezier("left",x)
                    self.bezierUpdates[x][2] = False
                if(self.bezierUpdates[x][3] == True):
                    self.updateBezier("right",x)
                    self.bezierUpdates[x][3] = False
                time.sleep(self.refreshrate)
    
    def getMidPoints(self, point1, point2):
        return ((float(point1[0])+float(point2[0]))/float(2), (float(point1[1])+float(point2[1]))/float(2))
    
    def oppControl(self, point, control):
        return (float(point[0])+(float(point[0])-float(control[0])),float(point[1])+(float(point[1])-float(control[1])))
    
    def reduceSide(self, circles, side, surface):
        if(len(circles)>3):
            count = (len(circles)-1)/2
            for x in list(reversed(range(0,count))):
                circle = circles[2*x+1]
                circles.pop(2*x+1)
                self.sender.removeElement(circle, 1)
            if(side == "top"):
                self.bezierUpdates[surface][0] = True
            elif(side == "bottom"):
                self.bezierUpdates[surface][1] = True
            elif(side == "left"):
                self.bezierUpdates[surface][2] = True
            elif(side == "right"):
                self.bezierUpdates[surface][3] = True
    
    def splitSide(self, circles, side, surface):
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
            self.bezierUpdates[surface][0] = True
        elif(side == "bottom"):
            self.bezierUpdates[surface][1] = True
        elif(side == "left"):
            self.bezierUpdates[surface][2] = True
        elif(side == "right"):
            self.bezierUpdates[surface][3] = True
            
    def updateBezier(self, side, surface):
        points = []
        circles = []
        if(side=="top"):
            circles = self.topCircles[surface]
        elif(side=="bottom"):
            circles = self.bottomCircles[surface]
        elif(side=="left"):
            circles = self.leftCircles[surface]
        elif(side=="right"):
            circles = self.rightCircles[surface]
        for x in range(0,len(circles)):
            pos = self.sender.getCirclePosition(circles[x])
            points.append((pos[0],pos[1]))
        calc = bezierCalc()
        if(side=="top"):
            curve = calc.getCurvePoints(points, self.ppe)
            self.sender.setLineStripContent(self.topbz[surface],curve)
        elif(side=="bottom"):
            curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
            self.sender.setLineStripContent(self.bottombz[surface],curve)
        elif(side=="left"):
            curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
            self.sender.setLineStripContent(self.leftbz[surface],curve)
        elif(side=="right"):
            curve = calc.getCurvePoints(points, self.ppe)
            self.sender.setLineStripContent(self.rightbz[surface],curve)
            
    def isHit(self, point1, point2):
        a = abs(float(point1[0])-float(point2[0]))
        b = abs(float(point1[1])-float(point2[1]))
        csq = pow(a,2) + pow(b,2)
        c = sqrt(csq)
        if (c<10):
            return True
        else:
            return False
        
    def updateMesh(self, surface):
        topPoints = []
        for x in range(0,len(self.topCircles[surface])):
            topPoints.append(self.sender.getCirclePosition(self.topCircles[surface][x]))
        bottomPoints = []
        for x in range(0,len(self.bottomCircles[surface])):
            bottomPoints.append(self.sender.getCirclePosition(self.bottomCircles[surface][len(self.bottomCircles[surface]) - 1 - x]))
        leftPoints = []
        for x in range(0,len(self.leftCircles[surface])):
            leftPoints.append(self.sender.getCirclePosition(self.leftCircles[surface][x]))
        rightPoints = []
        for x in range(0,len(self.rightCircles[surface])):
            rightPoints.append(self.sender.getCirclePosition(self.rightCircles[surface][len(self.rightCircles[surface]) - 1 - x]))
        self.sender.setSurfaceEdges(self.warpedSurf[surface], topPoints, bottomPoints, leftPoints, rightPoints)

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
                elif event.key==pygame.K_p:
                    self.defineSurface()
                    self.splitSide(self.topCircles[self.surfaceCounter-1], "top",self.surfaceCounter-1)
                    self.splitSide(self.bottomCircles[self.surfaceCounter-1], "bottom",self.surfaceCounter-1)
                    self.splitSide(self.leftCircles[self.surfaceCounter-1], "left",self.surfaceCounter-1)
                    self.splitSide(self.rightCircles[self.surfaceCounter-1], "right",self.surfaceCounter-1)
                elif event.key==pygame.K_SPACE:
                    for y in range(0,len(self.topCircles)):
                        self.updateMesh(y)
                elif event.key==pygame.K_ESCAPE:
                    self.sender.quit()
            if(self.mouseLock==True):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==4:
                        self.sender.rotateCursorClockwise(1,10)
                    elif event.button==5:
                        self.sender.rotateCursorAnticlockwise(1,10)
                    elif event.button==3:
                        self.rClickTime=datetime.datetime.now()
                        loc = self.sender.getCursorPosition(1)
                        self.rightDragging = []
                        for z in range(0,len(self.topCircles)):
                            point = self.sender.getCirclePosition(self.topCircles[z][0])
                            if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                self.rightDragging.append(self.topCircles[z][0])
                                
                            end = len(self.topCircles[z])-1
                            point = self.sender.getCirclePosition(self.topCircles[z][end])
                            if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                self.rightDragging.append(self.topCircles[z][end])
                             
                            point = self.sender.getCirclePosition(self.bottomCircles[z][0])
                            if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                self.rightDragging.append(self.bottomCircles[z][0])
                                
                            end = len(self.bottomCircles[z])-1
                            point = self.sender.getCirclePosition(self.bottomCircles[z][end])
                            if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                self.rightDragging.append(self.bottomCircles[z][end])
                            if(len(self.rightDragging)>0):
                                cirpos = self.sender.getCirclePosition(self.rightDragging[0])
                                self.symbolicDrag[0] = self.sender.newLine(1, cirpos[0], cirpos[1], loc[0], loc[1], (1, 0, 0, 1), 3)
                                self.symbolicDrag[1] = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 0, 0, 1), 20)
                    elif event.button==1:
                        self.lClickTime=datetime.datetime.now()
                        self.ldown=True
                        if(get_point==True):
                            loc = self.sender.getCursorPosition(1)
                            ele = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 0, 0, 1), 20)
                            return (loc, ele)
                        if(get_point!=True):
                            loc = self.sender.getCursorPosition(1)
                            self.dragging = []
                            for z in range(0,len(self.topCircles)):
                                for x in range(0,len(self.topCircles[z])):
                                    point = self.sender.getCirclePosition(self.topCircles[z][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.dragging.append(self.topCircles[z][x])
                                for x in range(0,len(self.bottomCircles[z])):
                                    point = self.sender.getCirclePosition(self.bottomCircles[z][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.dragging.append(self.bottomCircles[z][x])
                                for x in range(0,len(self.leftCircles[z])):
                                    point = self.sender.getCirclePosition(self.leftCircles[z][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.dragging.append(self.leftCircles[z][x])
                                for x in range(0,len(self.rightCircles[z])):
                                    point = self.sender.getCirclePosition(self.rightCircles[z][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.dragging.append(self.rightCircles[z][x])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if(event.button==1):
                        lClickRelTime=datetime.datetime.now()
                        self.ldown=False
                        elapsedSecs = (lClickRelTime-self.lClickTime).total_seconds()
                        if(elapsedSecs<0.15):
                            loc = self.sender.getCursorPosition(1)
                            for w in range(0,len(self.topCircles)):
                                for x in range(1,len(self.topCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.topCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.splitSide(self.topCircles[w], "top",w)
                                        self.updateMesh(w)
                                for x in range(1,len(self.bottomCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.bottomCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.splitSide(self.bottomCircles[w], "bottom",w)
                                        self.updateMesh(w)
                                for x in range(1,len(self.leftCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.leftCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.splitSide(self.leftCircles[w], "left",w)
                                        self.updateMesh(w)
                                for x in range(1,len(self.rightCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.rightCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        self.splitSide(self.rightCircles[w], "right",w)
                                        self.updateMesh(w)
                        for w in range(0,len(self.topCircles)):
                            if (len(self.topCircles[w])>1 and len(self.bottomCircles[w])>1 and len(self.leftCircles[w])>1 and len(self.rightCircles[w])>1):
                                self.dragging=[]
                                self.updateMesh(w)
                    if(event.button==3):
                        rClickRelTime=datetime.datetime.now()
                        elapsedSecs = (rClickRelTime-self.rClickTime).total_seconds()
                        hit = False
                        if(elapsedSecs<0.15):
                            loc = self.sender.getCursorPosition(1)
                            for w in range(0,len(self.topCircles)):
                                for x in range(1,len(self.topCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.topCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        hit = True
                                if (hit==True):
                                    hit=False
                                    self.reduceSide(self.topCircles[w], "top",w)
                                    self.updateMesh(w)
                                for x in range(1,len(self.bottomCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.bottomCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        hit = True
                                if (hit==True):
                                    hit=False
                                    self.reduceSide(self.bottomCircles[w], "bottom",w)
                                    self.updateMesh(w)
                                for x in range(1,len(self.leftCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.leftCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        hit = True
                                if (hit==True):
                                    hit=False
                                    self.reduceSide(self.leftCircles[w], "left",w)
                                    self.updateMesh(w)
                                for x in range(1,len(self.rightCircles[w])-1):
                                    point = self.sender.getCirclePosition(self.rightCircles[w][x])
                                    if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
                                        hit = True
                                if (hit==True):
                                    hit=False
                                    self.reduceSide(self.rightCircles[w], "right",w)
                                    self.updateMesh(w)
                        self.rightDragging=[]
                        if(len(self.symbolicDrag)>0):
                            self.sender.removeElement(self.symbolicDrag[0], 1)
                            self.sender.removeElement(self.symbolicDrag[1], 1)
                        self.symbolicDrag = {}       
                
                                                
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
                        for y in range(0,len(self.bezierUpdates)):
                            if(self.topCircles[y].__contains__(self.dragging[x])):
                                self.bezierUpdates[y][0] = True
                            if(self.bottomCircles[y].__contains__(self.dragging[x])):
                                self.bezierUpdates[y][1] = True
                            if(self.leftCircles[y].__contains__(self.dragging[x])):
                                self.bezierUpdates[y][2] = True
                            if(self.rightCircles[y].__contains__(self.dragging[x])):
                                self.bezierUpdates[y][3] = True
                if(len(self.rightDragging)!=0):
                    self.sender.relocateCircle(self.symbolicDrag[1], float(loc[0]), float(loc[1]), 1)
                    self.sender.setLineEnd(self.symbolicDrag[0], float(loc[0]), float(loc[1]))
        return None
    
    def defineSurface(self):
        tl = None
        bl = None
        tr = None
        br = None
        
        self.topCircles[self.surfaceCounter] = []
        self.bottomCircles[self.surfaceCounter] = []
        self.leftCircles[self.surfaceCounter] = []
        self.rightCircles[self.surfaceCounter] = []
        self.bezierUpdates[self.surfaceCounter] = [False,False,False,False]
        
        while(self.quit==False and tl==None):
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the top left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            tl = self.getInput(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        self.topCircles[self.surfaceCounter].append(tl[1])
        self.topbz[self.surfaceCounter] = self.sender.newLineStrip(1, tl[0][0], tl[0][1], (1,1,1,1), 5)
            
        while(self.quit==False and tr==None):
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the top right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            tr = self.getInput(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        self.topCircles[self.surfaceCounter].append(tr[1])
        self.sender.addLineStripPoint(self.topbz[self.surfaceCounter], tr[0][0], tr[0][1])
        self.rightCircles[self.surfaceCounter].append(tr[1])
        self.rightbz[self.surfaceCounter] = self.sender.newLineStrip(1, tr[0][0], tr[0][1], (1,1,1,1), 5)
            
        while(self.quit==False and br==None):
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the bottom right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            br = self.getInput(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        self.rightCircles[self.surfaceCounter].append(br[1])
        self.sender.addLineStripPoint(self.rightbz[self.surfaceCounter], br[0][0], br[0][1])
        self.bottomCircles[self.surfaceCounter].append(br[1])
        self.bottombz[self.surfaceCounter] = self.sender.newLineStrip(1, br[0][0], br[0][1], (1,1,1,1), 5)
            
        while(self.quit==False and bl==None):
            self.background.fill((255, 255, 255))
            text = self.font.render("Click the bottom left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            bl = self.getInput(True)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
        self.bottomCircles[self.surfaceCounter].append(bl[1])
        self.sender.addLineStripPoint(self.bottombz[self.surfaceCounter], bl[0][0], bl[0][1])
        self.leftCircles[self.surfaceCounter].append(bl[1])
        self.leftbz[self.surfaceCounter] = self.sender.newLineStrip(1, bl[0][0], bl[0][1], (1,1,1,1), 5)
        self.leftCircles[self.surfaceCounter].append(tl[1])
        self.sender.addLineStripPoint(self.leftbz[self.surfaceCounter], tl[0][0], tl[0][1])
        self.surfaceCounter += 1
    
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
        self.sender.showSetupSurface()
        self.warpedSurf[0] = self.sender.newSurface()
        self.sender.newWindow(0, 0, 1024, 1280, 1024, "setupWindow")
        self.sender.newCursor(0, 1280/2, 1024/2)
        
        window = self.sender.newWindow(self.warpedSurf[0], 200, 200, 100, 100, "Bob")
        self.sender.newCursor(self.warpedSurf[0], 512/2, 512/2)
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
        
        self.warpedSurf[1] = self.sender.newSurface()
        self.sender.newCursor(self.warpedSurf[1], 512/2, 512/2)
        window = self.sender.newWindow(self.warpedSurf[1], 200, 200, 100, 100, "Bob")
        self.sender.newTexRectangle(window, 200, 400, 300, 400, "american_gothic.jpg")
        self.sender.newRectangle(window, 50, 400, 100, 200, (1,1,1,1), (0.5,0.3,0.5,1))
        self.sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 100, 30, "Arial", (1,1,0,1))
        self.sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
        self.sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 200, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 300, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 400, 30, "Arial", (1,1,0,1))
        
        ele = self.sender.newPolygon(window, 100, 100, (1,1,1,1), (0.5,0.5,0.5,1))
        self.sender.addPolygonPoint(ele, 200, 150)
        self.sender.addPolygonPoint(ele, 200, 200)
        self.sender.addPolygonPoint(ele, 150, 175)
        self.sender.addPolygonPoint(ele, 75, 175)
        self.sender.addPolygonPoint(ele, 50, 150)
        #self.sender.addPolygonPoint(ele, 200, 150)
        #self.sender.addPolygonPoint(ele, 200, 150)
        
        self.warpedSurf[2] = self.sender.newSurface()
        self.sender.newCursor(self.warpedSurf[2], 512/2, 512/2)
        window = self.sender.newWindow(self.warpedSurf[2], 200, 200, 100, 100, "Bob")
        self.sender.newTexRectangle(window, 200, 400, 300, 400, "van_gough.jpg")
        self.sender.newRectangle(window, 50, 400, 100, 200, (1,1,1,1), (0.5,0.3,0.5,1))
        self.sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 100, 30, "Arial", (1,1,0,1))
        self.sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
        self.sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 200, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 300, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 400, 30, "Arial", (1,1,0,1))
        
        self.warpedSurf[3] = self.sender.newSurface()
        self.sender.newCursor(self.warpedSurf[3], 512/2, 512/2)
        window = self.sender.newWindow(self.warpedSurf[3], 200, 200, 100, 100, "Bob")
        self.sender.newTexRectangle(window, 200, 400, 300, 400, "the_scream.jpg")
        self.sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 100, 30, "Arial", (1,1,0,1))
        self.sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
        self.sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 200, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 300, 30, "Arial", (1,1,0,1))
        self.sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 400, 30, "Arial", (1,1,0,1))
        
        self.surfaceCounter = 0
        
        self.defineSurface()
        self.splitSide(self.topCircles[self.surfaceCounter-1], "top",self.surfaceCounter-1)
        self.splitSide(self.bottomCircles[self.surfaceCounter-1], "bottom",self.surfaceCounter-1)
        self.splitSide(self.leftCircles[self.surfaceCounter-1], "left",self.surfaceCounter-1)
        self.splitSide(self.rightCircles[self.surfaceCounter-1], "right",self.surfaceCounter-1)
        
        thread = threading.Thread(target=self.bezierUpdateTracker, args=()) #Creates the display thread
        thread.start() #Starts the display thread
        dirleft = True
        while(self.quit==False):
            self.background.fill((255, 255, 255))
            text = self.font.render("Press 'L' to release mouse", 1, (10, 10, 10))
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
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            self.getInput(False)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
client()