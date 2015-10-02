from Tkinter import *
from messageSender import *
import pygame
import threading
from threading import Thread
import time
from pygame.locals import *
import datetime
import tkMessageBox
import tkSimpleDialog

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
    currentTrackerData = ""

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
                        pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    #Runs if the left mouse button has been released
                    if(event.button==1):
                        lClickRelTime=datetime.datetime.now()
                        elapsedSecs = (lClickRelTime-self.lClickTime).total_seconds() #Checks how long the button was depressed
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
                xdist = (self.winWidth/2)-pos[0]
                ydist = (self.winHeight/2)-pos[1]
                if (not(xdist==0 and ydist==0)):
                    pygame.mouse.set_pos([self.winWidth/2,self.winHeight/2])
                    self.sender.shiftCursor(self.controlCur, -xdist, ydist)

    #Locks the mouse so that the server can be controlled
    def LockMouse(self):
        self.mouseLock = True
        pygame.mouse.set_visible(False)
        self.sender.showCursor(self.mainCur)

    def serverInit(self):
        CONNECTION_LIST = []
        RECV_BUFFER = 4096
        PORT = 5043

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #server_socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)
        server_socket.bind(("localhost", PORT))
        server_socket.listen(10)

        CONNECTION_LIST.append(server_socket)

        print "Chat server started on port " + str(PORT)

        while 1:
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

            for sock in read_sockets:
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                else:
                    try:
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            self.currentTrackerData = str(data)
                    except:
                        print "Client (%s, %s) is offline" % addr
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue

        server_socket.close()

    #Defines the GUI
    def tkinthread(self):
        self.master = Tk()
        d = MyDialog(self.master)
        self.username = d.getResult()
        self.master.wm_title("Cursor Program GUI")
        self.frame = Frame(self.master)
        self.frame.pack()
        self.slogan = Button(self.frame, text="Control Projected Mouse (Middle Click to Release)", command=self.LockMouse, width=40)
        self.slogan.pack(side=LEFT)
        self.master.mainloop()

    #Sets up the surfaces which can be defined within the client
    def initGUI(self):
        self.mainCur = self.sender.newCursor(1, 512/2, 512/2,"pix")
        self.controlCur = self.mainCur

    #The main loop
    def __init__(self):
        tkinterThread = threading.Thread(target=self.tkinthread, args=()) #Creates the display thread
        tkinterThread.start() #Starts the display thread

        thread = Thread(target=self.serverInit,args=())
        thread.start()

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

        self.sender.login(self.username)
        self.sender.setapp("CursorApp")
        self.sender.loadDefinedSurfaces("experimentLayout") #TODO Make layout file
        #TODO Load wall coordinates from file
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