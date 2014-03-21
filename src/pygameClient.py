from messageSender import *
import pygame
from pygame.locals import *

class client:

    def getInput(self):
        mpb=pygame.mouse.get_pressed() # mouse pressed buttons
        kpb=pygame.key.get_pressed() # keyboard pressed buttons
        pos=pygame.mouse.get_pos() # mouse shift
        for event in pygame.event.get():
            if event.type == QUIT:
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key==pygame.K_l:
                    if (self.mouseLock == True):
                        self.mouseLock = False
                        pygame.mouse.set_visible(True)
                    elif(self.mouseLock == False):
                        self.mouseLock = True
                        pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                        pygame.mouse.set_visible(False)
            if(self.mouseLock==True):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button==4:
                        self.sender.rotateCursorClockwise(1,10)
                    elif event.button==5:
                        self.sender.rotateCursorAnticlockwise(1,10)
                xdist = (self.winWidth/2)-pos[0]
                ydist = (self.winHeight/2)-pos[1]
                pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                virtualpos = self.sender.getCursorPosition(1)
                xloc = int(virtualpos["x"])-xdist
                yloc = int(virtualpos["y"])+ydist

                if (xloc<0):
                    xloc=0
                elif(xloc>self.winWidth):
                    xloc=self.winWidth
                if(yloc<0):
                    yloc = 0
                elif(yloc>self.winHeight):
                    yloc = self.winHeight
                self.sender.relocateCursor(1,xloc,yloc,0)
    
    def __init__(self):
        self.mouseLock = False
        self.sender = messageSender()
        self.winWidth = 1280
        self.winHeight = 1024
        
        # Initialise screen
        pygame.init()
        screen = pygame.display.set_mode((1280, 1024))
        pygame.display.set_caption('Basic Pygame program')
    
        # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))
    
        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("Hello There", 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        background.blit(text, textpos)
    
        # Blit everything to the screen
        screen.blit(background, (0, 0))
        pygame.display.flip()
    
        # Event loop
        while 1:
            self.getInput()
            screen.blit(background, (0, 0))
            pygame.display.flip()
            
client()