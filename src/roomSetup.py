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
    quit = False
    topCircles = []
    bottomCircles = []
    leftCircles = []
    rightCircles = []
    dragging = []
    
    def getMidPoints(self, point1, point2):
        return ((float(point1[0])+float(point2[0]))/float(2), (float(point1[1])+float(point2[1]))/float(2))
    
    def splitSide(self, circles):
        count = len(circles)
        insert = []
        for x in range(1, count):
            point1 = self.sender.getCirclePosition(circles[x-1])
            point2 = self.sender.getCirclePosition(circles[x])
            midpoint = self.getMidPoints((point1['x'],point1['y']), (point2['x'],point2['y']))
            insert.append(midpoint)
        for x in reversed(range(0,len(insert))):
            ele = self.sender.newCircle(1, insert[x][0], int(insert[x][1]), 10, (1, 0, 0, 1), (0, 1, 0, 1), 4)
            circles.insert(x+1, ele['elementNo'])
            
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
                    self.splitSide(self.topCircles)
                elif event.key==pygame.K_DOWN:
                    self.splitSide(self.bottomCircles)
                elif event.key==pygame.K_LEFT:
                    self.splitSide(self.leftCircles)
                elif event.key==pygame.K_RIGHT:
                    self.splitSide(self.rightCircles)
            if(self.mouseLock==True):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==4:
                        self.sender.rotateCursorClockwise(1,10)
                    elif event.button==5:
                        self.sender.rotateCursorAnticlockwise(1,10)
                    elif event.button==1:
                        if(get_point==True):
                            loc = self.sender.getCursorPosition(1)
                            ele = self.sender.newCircle(1, loc['x'], loc['y'], 10, (1, 0, 0, 1), (1, 0, 0, 1), 4)
                            return (loc, ele['elementNo'])
                        if(get_point!=True):
                            loc = self.sender.getCursorPosition(1)
                            self.dragging = []
                            for x in range(0,len(self.topCircles)):
                                point = self.sender.getCirclePosition(self.topCircles[x])
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append(self.topCircles[x])
                            for x in range(0,len(self.bottomCircles)):
                                point = self.sender.getCirclePosition(self.bottomCircles[x])
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append(self.bottomCircles[x])
                            for x in range(0,len(self.leftCircles)):
                                point = self.sender.getCirclePosition(self.leftCircles[x])
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append(self.leftCircles[x])
                            for x in range(0,len(self.rightCircles)):
                                point = self.sender.getCirclePosition(self.rightCircles[x])
                                if(self.isHit((point['x'],point['y']),(loc["x"],loc["y"]))):
                                    self.dragging.append(self.rightCircles[x])
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
                        print self.dragging[x]
                        self.sender.relocateCircle(self.dragging[x], float(loc["x"]), float(loc["y"]), 1)
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
        
        self.sender.newText(1, "Arial", 100, 100, 30, "Arial", (1,1,0,1))
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
        self.rightCircles.append(tr[1])
            
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
        self.bottomCircles.append(br[1])
            
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
        self.leftCircles.append(bl[1])
        self.leftCircles.append(tl[1])
        
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