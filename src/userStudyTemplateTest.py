from Tkinter import *
from trackedMessageSender import *
import pygame
import threading
import time
from pygame.locals import *
import datetime
import tkMessageBox
import tkSimpleDialog
import random

class MyDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(master, text="User Name:").grid(row=0)
        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus

    def apply(self):
        user = self.e1.get()
        self.result = (user)
        
    def getResult(self):
        return self.result

class client:
    __slots__ = ['ppe']
    quit = False
    refreshrate = 0
    mainCur = None
    controlCur = None
    username = None
    notes1 = []
    notes2 = []
    nextnote1 = 0
    nextnote2 = 0
    dragging = []
    controlWall = 1
            
    #Checks for mouse button and keyboard
    def getInput(self,get_point):
        pos=pygame.mouse.get_pos() # mouse shift
        for event in pygame.event.get():
            if event.type == QUIT:
                    self.quit = True
                    return None
            elif event.type == pygame.KEYDOWN:
                pass
            if(self.mouseLock==True):
                #Runs if a mouse button has been depressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #Runs if the mouse wheel is being rolled upwards
                    if event.button==4:
                        pass
                    elif event.button==5:
                        pass
                    #Runs if the middle mouse button is pressed
                    elif event.button==2:
                        self.mClickTime=datetime.datetime.now() #Saves the current time so that when the button is released click duration can be checked
                        pass
                    #Runs if the right mouse button is pressed
                    elif event.button==3:
                        self.rClickTime=datetime.datetime.now() #Saves the current time so that when the button is released click duration can be checked
                        pass
                    #runs if the left mouse button is pressed
                    elif event.button==1:
                        self.lClickTime=datetime.datetime.now() #Saves the current time so that when the button is released click duration can be checked
                        wall = None
                        if(self.controlWall==1):
                            wall = self.notes1
                        else:
                            wall = self.notes2
                        clickpos = self.sender.getCursorPosition(self.mainCur)
                        for note in range(0,len(wall)):
                            if(clickpos[0]>wall[note][1] and clickpos[0]<(wall[note][1]+wall[note][3])):
                                if(clickpos[1]<wall[note][2] and clickpos[1]>(wall[note][2]-wall[note][3])):
                                    self.dragging.append(note)
                                    print "HIT!"
                        pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    #Runs if the left mouse button has been released
                    if(event.button==1):
                        lClickRelTime=datetime.datetime.now()
                        elapsedSecs = (lClickRelTime-self.lClickTime).total_seconds() #Checks how long the button was depressed
                        self.dragging = []
                        if(elapsedSecs<0.15):
                            pass
                        else:
                            pass
                    #Runs if the middle mouse button has been released
                    if(event.button==2):
                        mClickRelTime=datetime.datetime.now()
                        elapsedSecs = (mClickRelTime-self.mClickTime).total_seconds() #Checks how long the button was depressed
                        if(elapsedSecs<0.25):
                            self.mouseLock = False
                            pygame.mouse.set_visible(True)
                            self.master.focus_force()
                            self.sender.hideCursor(self.mainCur)
                        else:
                            pass
                                
                    #Runs if the right mouse button has been released
                    if(event.button==3):
                        rClickRelTime=datetime.datetime.now()
                        elapsedSecs = (rClickRelTime-self.rClickTime).total_seconds() #Checks how long the button was depressed
                        if(elapsedSecs<0.15):
                            pass
                        else:
                            pass
        return None
    
    #Loops until the program is closed and monitors mouse movement
    def mouseMovement(self):
        while(self.quit==False):
            time.sleep(1.0/60)
            if(self.mouseLock==True):
                pos=pygame.mouse.get_pos()
                xdist = -((self.winWidth/2)-pos[0])
                ydist = (self.winHeight/2)-pos[1]
                if (not(xdist==0 and ydist==0)):
                    pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                    self.sender.shiftCursor(self.mainCur, xdist, ydist)
                    if(len(self.dragging)>0):
                        dragnote = self.dragging[len(self.dragging)-1]
                        if(self.controlWall==1):
                            self.sender.shiftWindow(self.notes1[dragnote][0], xdist, ydist, "pix")
                            self.notes1[dragnote]=(self.notes1[dragnote][0],self.notes1[dragnote][1]+xdist,self.notes1[dragnote][2]+ydist,self.notes1[dragnote][3])
                        else:
                            self.sender.shiftWindow(self.notes2[dragnote][0], xdist, ydist, "pix")
                            self.notes1[dragnote]=(self.notes2[dragnote][0],self.notes2[dragnote][1]+xdist,self.notes2[dragnote][2]+ydist,self.notes2[dragnote][3])
                            
    
    #Locks the mouse so that the server can be controlled
    def LockMouse(self):
        self.mouseLock = True
        pygame.mouse.set_visible(False)
        self.sender.showCursor(self.mainCur)
    
    #Defines the GUI
    def tkinthread(self):
        self.master = Tk()
        d = MyDialog(self.master)
        self.username = d.getResult()
        self.master.wm_title("Cursor Program GUI")
        self.frame = Frame(self.master)
        self.frame.pack()
        self.contwall1but = Button(self.frame, text="Control Wall 1 Cursor", command=self.wall1move, width=17)
        self.contwall1but.pack(side=LEFT)
        self.contwall2but = Button(self.frame, text="Control Wall 2 Cursor", command=self.wall2move, width=17)
        self.contwall2but.pack(side=LEFT)
        self.frame1 = Frame(self.master)
        self.frame1.pack()
        text = Text(self.frame1, height=1, width=42, fg='white', bg='black', relief='flat')
        text.insert(END, "Press middle mouse button to release mouse")
        text.pack()
        self.frame2 = Frame(self.master)
        self.frame2.pack()
        self.textbox = Entry(self.frame2, width=40)
        self.textbox.pack(side=LEFT)
        self.frame3 = Frame(self.master)
        self.frame3.pack()        
        self.wall1but = Button(self.frame3, text="Add to Wall 1", command=self.wall1add, width=17)
        self.wall1but.pack(side=LEFT)
        self.wall2but = Button(self.frame3, text="Add to Wall 2", command=self.wall2add, width=17)
        self.wall2but.pack(side=RIGHT)
        self.master.mainloop()
    
    #Sets up the surfaces which can be defined within the client
    def initGUI(self):
        self.mainCur = self.sender.newCursor(1, self.sender.getSurfacePixelWidth(1)/2, self.sender.getSurfacePixelHeight(1)/2, "pix")
        self.controlCur = self.mainCur
        
    def wall1move(self):
        self.sender.relocateCursor(self.mainCur, self.sender.getSurfacePixelWidth(1)/2, self.sender.getSurfacePixelHeight(1)/2, 1)
        self.controlWall = 1
        self.LockMouse()
        
    def wall2move(self):
        self.sender.relocateCursor(self.mainCur, self.sender.getSurfacePixelWidth(2)/2, self.sender.getSurfacePixelHeight(2)/2, 2)
        self.controlWall = 2
        self.LockMouse()
        
    def wall1add(self):
        noteWidth = int(self.sender.getTextWidth(self.textbox.get(), "Arial", 20))
        x = random.randint(0,self.sender.getSurfacePixelWidth(1)-noteWidth)
        y = random.randint(0+noteWidth,self.sender.getSurfacePixelHeight(1))
        self.notes1.append((self.sender.newWindow(1, x, y, noteWidth, noteWidth, "pix", "note"), x, y, noteWidth))
        self.sender.newRectangle(self.notes1[self.nextnote1][0], 0, noteWidth, noteWidth, noteWidth, "pix", (0,0,0,0), 0, (1,1,0,1))
        self.sender.newText(self.notes1[self.nextnote1][0], self.textbox.get(), 0, noteWidth-self.sender.getTextLineHeight("Arial", 20), "pix", 20, "Arial", (0,0,0,1))
        self.nextnote1+=1
        
    def wall2add(self):
        noteWidth = int(self.sender.getTextWidth(self.textbox.get(), "Arial", 20))
        x = random.randint(0,self.sender.getSurfacePixelWidth(2)-noteWidth)
        y = random.randint(0+noteWidth,self.sender.getSurfacePixelHeight(2))
        self.notes2.append((self.sender.newWindow(2, x, y, noteWidth, noteWidth, "pix", "note"), x, y, noteWidth))
        self.sender.newRectangle(self.notes2[self.nextnote2][0], 0, noteWidth, noteWidth, noteWidth, "pix", (0,0,0,0), 0, (1,1,0,1))
        self.sender.newText(self.notes2[self.nextnote2][0], self.textbox.get(), 0, noteWidth-self.sender.getTextLineHeight("Arial", 20), "pix", 20, "Arial", (0,0,0,1))
        self.nextnote2+=1

    #The main loop
    def __init__(self):
        tkinterThread = threading.Thread(target=self.tkinthread, args=()) #Creates the display thread
        tkinterThread.start() #Starts the display thread
        
        self.sender = messageSender()
        self.winWidth = 320
        self.winHeight = 240
        
        # Initialise screen
        pygame.init()
        self.screen = pygame.display.set_mode((self.winWidth, self.winHeight))
        pygame.display.set_caption('Cursor Program')
    
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
        
        while(self.username==None):
            pass
        
        #Initial Setup
        self.sender.login(self.username)
        self.sender.setapp("study")
        self.initGUI()
        
        self.mouseLock=False
        pygame.mouse.set_visible(False)
        
        mouseThread = threading.Thread(target=self.mouseMovement, args=()) #Creates the display thread
        mouseThread.start() #Starts the display thread
        
        if(self.quit==False):
            while(self.quit==False):
                self.background.fill((255, 255, 255))
                text = self.font.render("", 1, (10, 10, 10))
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