from messageSender import *
import pygame
import threading
import time
from pygame.locals import *
from math import *
from bezier import *
from ConfigParser import SafeConfigParser
import datetime

class client:
    quit = False
    refreshrate = 0

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
                elif event.key==pygame.K_ESCAPE:
                    self.sender.quit()
                    time.sleep(0.1)
                    self.quit = True
        return None
    
    def mouseMovement(self):
        while(self.quit==False):
            time.sleep(1.0/60)
            if(self.mouseLock==True):
                pos=pygame.mouse.get_pos()
                xdist = (self.winWidth/2)-pos[0]
                ydist = (self.winHeight/2)-pos[1]
                if (not(xdist==0 and ydist==0)):
                    pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                    
                    self.sender.shiftCursor(self.currentCur, -xdist, ydist)
        
    def blueCircleAnimation(self):
        while(self.quit==False):
            time.sleep(1.0/30)
            pos = self.sender.getCirclePosition(self.blueCirc)
            if(pos[0]>=self.sender.getSurfacePixelWidth(1)):
                self.dirleft = False
            if(pos[0]<=0):
                self.dirleft = True
            if(self.dirleft):
                self.sender.relocateCircle(self.blueCirc, pos[0]+5, pos[1], "pix", self.window)
            else:
                self.sender.relocateCircle(self.blueCirc, pos[0]-5, pos[1], "pix", self.window)
    
    def __init__(self):
        self.sender = messageSender()
        self.winWidth = 320
        self.winHeight = 240
        
        # Initialise screen
        pygame.init()
        self.screen = pygame.display.set_mode((self.winWidth, self.winHeight))
        pygame.display.set_caption('Independent Program')
    
        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255, 255, 255))
    
        # Display some text
        self.font = pygame.font.Font(None, 36)

        # Blit everything to the screen
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        
        self.sender.login("jp438")
        self.sender.setapp("indapp")
        #self.sender.loadDefinedSurfaces("spaceSave")
        
        window1 = self.sender.newWindow(1, 0, 512, 512, 512, "pix", "Bob")
        self.currentCur = self.sender.newCursor(1, 512/2, 512/2, "pix")
        
        self.sender.newTexRectangle(window1, 200, 400, 300, 400, "pix", "Mona_Lisa.jpg")
        self.sender.newRectangle(window1, 50, 400, 100, 200, "pix", (1,1,1,1), 0, (0.5,0.3,0.5,1))
        self.sender.newCircle(window1, 50, 50, 50, "pix", (1,1,1,1), 10, (1,0,1,1), 50)
        self.sender.newCircle(window1, 250, 100, 50, "pix", (1,1,1,1), 0, (0,1,0,1), 50)
        self.sender.newCircle(window1, 415, 250, 50, "pix", (1,1,1,1), 0, (1,1,0,1), 50)
        self.sender.newCircle(window1, 200, 200, 50, "pix", (1,1,1,1), 0, (1,0,0,1), 50)
        
        self.blueCirc = self.sender.newCircle(window1, 0.5, 0.5, 0.1, "prop", (1,1,1,1), 0, (0,0,1,1), 50)
        
        self.sender.newCircle(window1, 300, 512, 50, "pix", (1,1,1,1), 0, (0.5,0.5,0.5,1), 50)
        
        self.sender.newText(window1, "Hello World  | dlroW olleH", 100, 100, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newLine(window1, 0, 0, 512, 512, "pix", (0,1,1,1), 2)
        self.sender.newText(window1, "Hello World  | dlroW olleH", 100, 200, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window1, "Hello World  | dlroW olleH", 100, 300, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window1, "Hello World  | dlroW olleH", 100, 400, "pix", 30, "Arial", (1,1,0,1))
        
        ele = self.sender.newPolygon(window1, 100, 100, "pix", (1,1,1,1), 0, (0.5,0.5,0.5,1))
        self.sender.addPolygonPoint(ele, 200, 150, "pix")
        self.sender.addPolygonPoint(ele, 200, 200, "pix")
        self.sender.addPolygonPoint(ele, 150, 175, "pix")
        self.sender.addPolygonPoint(ele, 75, 175, "pix")
        self.sender.addPolygonPoint(ele, 50, 150, "pix")
        
        
        window2 = self.sender.newWindow(2, 0, 512, 512, 512, "pix", "Bob")
        self.sender.newTexRectangle(window2, 200, 400, 300, 400, "pix", "american_gothic.jpg")
        self.sender.newRectangle(window2, 50, 400, 100, 200, "pix", (1,1,1,1), 0, (0.5,0.3,0.5,1))
        self.sender.newText(window2, "Goodbye circles  | selcric eybdooG", 30, 100, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newLine(window2, 0, 0, 512, 512, "pix", (0,1,1,1), 2)
        self.sender.newText(window2, "Goodbye circles  | selcric eybdooG", 30, 200, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window2, "Goodbye circles  | selcric eybdooG", 30, 300, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window2, "Goodbye circles  | selcric eybdooG", 30, 400, "pix", 30, "Arial", (1,1,0,1))
        
        ele = self.sender.newPolygon(window2, 100, 100, "pix", (1,1,1,1), 0, (0.5,0.5,0.5,1))
        self.sender.addPolygonPoint(ele, 200, 150, "pix")
        self.sender.addPolygonPoint(ele, 200, 200, "pix")
        self.sender.addPolygonPoint(ele, 150, 175, "pix")
        self.sender.addPolygonPoint(ele, 75, 175, "pix")
        self.sender.addPolygonPoint(ele, 50, 150, "pix")

        window3 = self.sender.newWindow(3, 0, 512, 512, 512, "pix", "Bob")
        self.sender.newTexRectangle(window3, 200, 400, 300, 400, "pix", "van_gough.jpg")
        self.sender.newRectangle(window3, 50, 400, 100, 200, "pix", (1,1,1,1), 0, (0.5,0.3,0.5,1))
        self.sender.newText(window3, "Goodbye polygon  | nogylop eybdooG", 30, 100, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newLine(window3, 0, 0, 512, 512, "pix", (0,1,1,1), 2)
        self.sender.newText(window3, "Goodbye polygon  | nogylop eybdooG", 30, 200, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window3, "Goodbye polygon  | nogylop eybdooG", 30, 300, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window3, "Goodbye polygon  | nogylop eybdooG", 30, 400, "pix", 30, "Arial", (1,1,0,1))
        
        window4 = self.sender.newWindow(4, 0, 512, 512, 512, "pix", "Bob")
        self.sender.newTexRectangle(window4, 200, 400, 300, 400, "pix", "the_scream.jpg")
        self.sender.newText(window4, "Goodbye rectangle  | elgnatcer eybdooG", 30, 100, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newLine(window4, 0, 0, 512, 512, "pix", (0,1,1,1), 2)
        self.sender.newText(window4, "Goodbye rectangle  | elgnatcer eybdooG", 30, 200, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window4, "Goodbye rectangle  | elgnatcer eybdooG", 30, 300, "pix", 30, "Arial", (1,1,0,1))
        self.sender.newText(window4, "Goodbye rectangle  | elgnatcer eybdooG", 30, 400, "pix", 30, "Arial", (1,1,0,1))
        
        self.mouseLock=True
        pygame.mouse.set_visible(False)
        
        mouseThread = threading.Thread(target=self.mouseMovement, args=()) #Creates the display thread
        mouseThread.start() #Starts the display thread
        
        if(self.quit==False):
            self.dirleft = True
            self.window = window1
            circAnim = threading.Thread(target=self.blueCircleAnimation, args=()) #Creates the display thread
            circAnim.start() #Starts the display thread
            while(self.quit==False):
                self.background.fill((255, 255, 255))
                text = self.font.render("Press 'L' to release mouse", 1, (10, 10, 10))
                textpos = text.get_rect()
                textpos.centerx = self.background.get_rect().centerx
                self.background.blit(text, textpos)
                self.getInput(False)
                self.screen.blit(self.background, (0, 0))
                pygame.display.flip()
                time.sleep(1/30)
        time.sleep(0.2)
        pygame.quit()
client()