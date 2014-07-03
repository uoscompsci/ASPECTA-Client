from messageSender import *
import pygame
from pygame.locals import *
from math import *

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
    __slots__ = ['tl','tr','br','bl','top','right','bottom','left']
    quit = False
    tl = None
    tr = None
    br = None
    bl = None
    top = []
    bottom = []
    left = []
    right = []
    topCircles = []
    bottomCircles = []
    leftCircles = []
    rightCircles = []
    dragging = []
    
    def getMidPoints(self, point1, point2):
        return ((point1[0]+point2[0])/float(2), (point1[1]+point2[1])/float(2))
    
    def splitSide(self, side, circles):
        count = int(self.sender.getLineStripPointCount(side['elementNo'])['count'])
        insert = []
        for x in range(1, count):
            point1 = self.sender.getLineStripPoint(side['elementNo'], x-1)
            point2 = self.sender.getLineStripPoint(side['elementNo'], x)
            midpoint = self.getMidPoints((point1['x'],point1['y']), (point2['x'],point2['y']))
            insert.append(midpoint)
        for x in reversed(range(0,len(insert))):
            self.sender.addLineStripPointAt(side['elementNo'], int(insert[x][0]), int(insert[x][1]), x+1)
            ele = self.sender.newCircle(1, insert[x][0], int(insert[x][1]), 10, "blue", "blue", 12)
            if(circles == "top"):
                self.topCircles.insert(x+1, ele['elementNo'])
            elif(circles == "bottom"):
                self.bottomCircles.insert(x+1, ele['elementNo'])
            elif(circles == "left"):
                self.leftCircles.insert(x+1, ele['elementNo'])
            elif(circles == "right"):
                self.rightCircles.insert(x+1, ele['elementNo'])
            
    def isHit(self, point1, point2):
        a = abs(point1[0]-point2[0])
        b = abs(point1[1]-point2[1])
        csq = pow(a,2) + pow(b,2)
        c = sqrt(csq)
        if (c<10):
            return True
        else:
            return False

    def getInput(self,get_point):
        mpb=pygame.mouse.get_pressed() # mouse pressed buttons
        kpb=pygame.key.get_pressed() # keyboard pressed buttons
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
                    self.splitSide(self.top,"top")
                elif event.key==pygame.K_DOWN:
                    self.splitSide(self.bottom,"bottom")
                elif event.key==pygame.K_LEFT:
                    self.splitSide(self.left,"left")
                elif event.key==pygame.K_RIGHT:
                    self.splitSide(self.right,"right")
            if(self.mouseLock==True):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==4:
                        self.sender.rotateCursorClockwise(1,10)
                    elif event.button==5:
                        self.sender.rotateCursorAnticlockwise(1,10)
                    elif event.button==1:
                        if(get_point==True):
                            loc = self.sender.getCursorPosition(1)
                            ele = self.sender.newCircle(1, loc['x'], loc['y'], 10, "blue", "blue", 12)
                            return (loc, ele['elementNo'])
                        if(get_point!=True):
                            loc = self.sender.getCursorPosition(1)
                            self.dragging = []
                            for x in range(0,self.sender.getLineStripPointCount(self.top['elementNo'])['count']):
                                point = self.sender.getLineStripPoint(self.top['elementNo'], x)
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append((int(self.top["elementNo"]),x))
                            for x in range(0,self.sender.getLineStripPointCount(self.bottom['elementNo'])['count']):
                                point = self.sender.getLineStripPoint(self.bottom['elementNo'], x)
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append((int(self.bottom["elementNo"]),x))
                            for x in range(0,self.sender.getLineStripPointCount(self.left['elementNo'])['count']):
                                point = self.sender.getLineStripPoint(self.left['elementNo'], x)
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append((int(self.left["elementNo"]),x))
                            for x in range(0,self.sender.getLineStripPointCount(self.right['elementNo'])['count']):
                                point = self.sender.getLineStripPoint(self.right['elementNo'], x)
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append((int(self.right["elementNo"]),x))
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button==1:
                        self.dragging=[]
                        
                xdist = (self.winWidth/2)-pos[0]
                ydist = (self.winHeight/2)-pos[1]
                pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                
                loc = self.sender.testMoveCursor(1,-xdist,ydist)

                if (loc['x']<0):
                    loc['x']=0
                elif(loc['x']>1280):
                    loc['x']=1280
                if(loc['y']<0):
                    loc['y'] = 0
                elif(loc['y']>1024):
                    loc['y'] = 1024
                self.sender.relocateCursor(1,loc['x'],loc['y'],0)
                if(len(self.dragging)!=0):
                    for x in range (0,len(self.dragging)):
                        self.sender.moveLineStripPoint(self.dragging[x][0], self.dragging[x][1], float(loc["x"]), float(loc["y"]))
                        if(int(self.dragging[x][0])==int(self.top['elementNo'])):
                            self.sender.relocateCircle(self.topCircles[int(self.dragging[x][1])], float(loc["x"]), float(loc["y"]), 1)
                        elif(int(self.dragging[x][0])==int(self.bottom['elementNo'])):
                            self.sender.relocateCircle(self.bottomCircles[int(self.dragging[x][1])], float(loc["x"]), float(loc["y"]), 1)
                        elif(int(self.dragging[x][0])==int(self.left['elementNo'])):
                            self.sender.relocateCircle(self.leftCircles[int(self.dragging[x][1])], float(loc["x"]), float(loc["y"]), 1)
                        elif(int(self.dragging[x][0])==int(self.right['elementNo'])):
                            self.sender.relocateCircle(self.rightCircles[int(self.dragging[x][1])], float(loc["x"]), float(loc["y"]), 1)
        return None
    
    def __init__(self):
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
        self.sender.newWindow(0, 0, 1024, 1280, 1024, "setupWindow")
        self.sender.newCursor(0, 1280/2, 1024/2)

        self.mouseLock=True
        pygame.mouse.set_visible(False)
        
        self.sender.newText(1, "Arial", 100, 100, 30, "Arial", "red")
        
        while(self.quit==False and self.tl==None):
            background.fill((255, 255, 255))
            text = font.render("Click the top left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.tl = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.topCircles.append(self.tl[1])
        self.top = self.sender.newLineStrip(1, self.tl[0]['x'], self.tl[0]['y'], 'blue', 5)
            
        while(self.quit==False and self.tr==None):
            background.fill((255, 255, 255))
            text = font.render("Click the top right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.tr = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.topCircles.append(self.tr[1])
        self.sender.addLineStripPoint(self.top['elementNo'], self.tr[0]['x'], self.tr[0]['y'])
        self.rightCircles.append(self.tr[1])
        self.right = self.sender.newLineStrip(1, self.tr[0]['x'], self.tr[0]['y'], 'blue', 5)
            
        while(self.quit==False and self.br==None):
            background.fill((255, 255, 255))
            text =font.render("Click the bottom right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.br = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.rightCircles.append(self.br[1])
        self.sender.addLineStripPoint(self.right['elementNo'], self.br[0]['x'], self.br[0]['y'])
        self.bottomCircles.append(self.br[1])
        self.bottom = self.sender.newLineStrip(1, self.br[0]['x'], self.br[0]['y'], 'blue', 5)
            
        while(self.quit==False and self.bl==None):
            background.fill((255, 255, 255))
            text = font.render("Click the bottom left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.bl = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.bottomCircles.append(self.bl[1])
        self.sender.addLineStripPoint(self.bottom['elementNo'], self.bl[0]['x'], self.bl[0]['y'])
        self.leftCircles.append(self.bl[1])
        self.left = self.sender.newLineStrip(1, self.bl[0]['x'], self.bl[0]['y'], 'blue', 5)
        self.leftCircles.append(self.tl[1])
        self.sender.addLineStripPoint(self.left['elementNo'], self.tl[0]['x'], self.tl[0]['y'])
        
        while(self.quit==False):
            background.fill((255, 255, 255))
            text = font.render("Press 'L' to release mouse", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.getInput(False)
            screen.blit(background, (0, 0))
            pygame.display.flip()
client()