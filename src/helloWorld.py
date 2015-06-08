from messageSender import *

sender = messageSender()
sender.login("username")
sender.setapp("helloworld")
height = sender.getSurfacePixelHeight(1)
width = sender.getSurfacePixelWidth(1)
win = sender.newWindow(1, 0, height, width, height, "pix", "HW")
sender.newText(win, "Hello World", height/2-150, width/2-25, "pix", 60, "Free Sans", (1,1,1,1))