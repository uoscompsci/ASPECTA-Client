from messageSender import *
import pygame
from pygame.locals import *

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
    dragging = 0

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
            if(self.mouseLock==True):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==4:
                        self.sender.rotateCursorClockwise(1,10)
                    elif event.button==5:
                        self.sender.rotateCursorAnticlockwise(1,10)
                    elif event.button==1:
                        if(get_point==True):
                            loc = self.sender.getCursorPosition(1)
                            ele = self.sender.newCircle(1, loc['x'], loc['y'], 10, "blue", "blue")
                            return (loc, ele)
                        if(get_point!=True):
                            loc = self.sender.getCursorPosition(1)
                            elements = self.sender.getClickedElements(0, loc["x"], loc["y"])
                            if (len(elements)!=0):
                                self.dragging = int(elements["0"])
                            else:
                                self.dragging=0
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button==1:
                        self.dragging=0
                        
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
                if(self.dragging!=0):
                    type = self.sender.getElementType(self.dragging)
                    if(type["type"]=="circle"):
                        self.sender.relocateCircle(self.dragging, float(loc['x']), float(loc['y']), 1)
                        if(self.dragging==self.tl[1]['elementNo']):
                            self.sender.moveLineStripPoint(self.top['elementNo'], 1, float(loc['x']), float(loc['y']))
                            self.sender.moveLineStripPoint(self.left['elementNo'], 2, float(loc['x']), float(loc['y']))
                        if(self.dragging==self.tr[1]['elementNo']):
                            self.sender.moveLineStripPoint(self.top['elementNo'], 2, float(loc['x']), float(loc['y']))
                            self.sender.moveLineStripPoint(self.right['elementNo'], 1, float(loc['x']), float(loc['y']))
                        if(self.dragging==self.br[1]['elementNo']):
                            self.sender.moveLineStripPoint(self.right['elementNo'], 2, float(loc['x']), float(loc['y']))
                            self.sender.moveLineStripPoint(self.bottom['elementNo'], 1, float(loc['x']), float(loc['y']))
                        if(self.dragging==self.bl[1]['elementNo']):
                            self.sender.moveLineStripPoint(self.bottom['elementNo'], 2, float(loc['x']), float(loc['y']))
                            self.sender.moveLineStripPoint(self.left['elementNo'], 1, float(loc['x']), float(loc['y']))
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
        
        self.sender.showSetupSurface()
        self.sender.newWindow(0, 0, 1024, 1280, 1024, "setupWindow")
        self.sender.newCursor(0, 1280/2, 1024/2)

        self.mouseLock=True
        pygame.mouse.set_visible(False)
        
        while(self.quit==False and self.tl==None):
            background.fill((255, 255, 255))
            text = font.render("Click the top left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.tl = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.top = self.sender.newLineStrip(1, self.tl[0]['x'], self.tl[0]['y'], 'blue')
            
        while(self.quit==False and self.tr==None):
            background.fill((255, 255, 255))
            text = font.render("Click the top right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.tr = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.sender.addLineStripPoint(self.top['elementNo'], self.tr[0]['x'], self.tr[0]['y'])
        self.right = self.sender.newLineStrip(1, self.tr[0]['x'], self.tr[0]['y'], 'blue')
            
        while(self.quit==False and self.br==None):
            background.fill((255, 255, 255))
            text =font.render("Click the bottom right", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.br = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.sender.addLineStripPoint(self.right['elementNo'], self.br[0]['x'], self.br[0]['y'])
        self.bottom = self.sender.newLineStrip(1, self.br[0]['x'], self.br[0]['y'], 'blue')
            
        while(self.quit==False and self.bl==None):
            background.fill((255, 255, 255))
            text = font.render("Click the bottom left", 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)
            self.bl = self.getInput(True)
            screen.blit(background, (0, 0))
            pygame.display.flip()
        self.sender.addLineStripPoint(self.bottom['elementNo'], self.bl[0]['x'], self.bl[0]['y'])
        self.left = self.sender.newLineStrip(1, self.bl[0]['x'], self.bl[0]['y'], 'blue')
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