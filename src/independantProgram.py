from messageSender import *
import time

dirleft=True

warpedSurf = {}
sender = messageSender()
sender.login("jp438")
sender.setapp("myapp")
sender.loadDefinedSurfaces("spaceSave")

window = sender.newWindow(1, 200, 200, 100, 100, "Bob")
sender.newCursor(1, 512/2, 512/2)
sender.newTexRectangle(window, 200, 400, 300, 400, "Mona_Lisa.jpg")
sender.newRectangle(window, 50, 400, 100, 200, (1,1,1,1), (0.5,0.3,0.5,1))
sender.newCircle(window, 50, 50, 50, (1,1,1,1), (1,0,1,1), 50)
sender.newCircle(window, 250, 100, 50, (1,1,1,1), (0,1,0,1), 50)
sender.newCircle(window, 415, 250, 50, (1,1,1,1), (1,1,0,1), 50)
sender.newCircle(window, 200, 200, 50, (1,1,1,1), (1,0,0,1), 50)
blueCirc = sender.newCircle(window, 400, 300, 50, (1,1,1,1), (0,0,1,1), 50)
sender.newCircle(window, 300, 512, 50, (1,1,1,1), (0.5,0.5,0.5,1), 50)

#self.sender.newRectangle(window, 200, 200, 100, 200, (1,1,1,1), (0,0,1,1))

sender.newText(window, "Hello World  | dlroW olleH", 100, 100, 30, "Arial", (1,1,0,1))
sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
sender.newText(window, "Hello World  | dlroW olleH", 100, 200, 30, "Arial", (1,1,0,1))
sender.newText(window, "Hello World  | dlroW olleH", 100, 300, 30, "Arial", (1,1,0,1))
sender.newText(window, "Hello World  | dlroW olleH", 100, 400, 30, "Arial", (1,1,0,1))

ele = sender.newPolygon(window, 100, 100, (1,1,1,1), (0.5,0.5,0.5,1))
sender.addPolygonPoint(ele, 200, 150)
sender.addPolygonPoint(ele, 200, 200)
sender.addPolygonPoint(ele, 150, 175)
sender.addPolygonPoint(ele, 75, 175)
sender.addPolygonPoint(ele, 50, 150)
#self.sender.addPolygonPoint(ele, 200, 150)
#self.sender.addPolygonPoint(ele, 200, 150)

#self.sender.newCursor(self.warpedSurf[1], 512/2, 512/2)
window = sender.newWindow(2, 200, 200, 100, 100, "Bob")
sender.newTexRectangle(window, 200, 400, 300, 400, "american_gothic.jpg")
sender.newRectangle(window, 50, 400, 100, 200, (1,1,1,1), (0.5,0.3,0.5,1))
sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 100, 30, "Arial", (1,1,0,1))
sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 200, 30, "Arial", (1,1,0,1))
sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 300, 30, "Arial", (1,1,0,1))
sender.newText(window, "Goodbye circles  | selcric eybdooG", 30, 400, 30, "Arial", (1,1,0,1))

ele = sender.newPolygon(window, 100, 100, (1,1,1,1), (0.5,0.5,0.5,1))
sender.addPolygonPoint(ele, 200, 150)
sender.addPolygonPoint(ele, 200, 200)
sender.addPolygonPoint(ele, 150, 175)
sender.addPolygonPoint(ele, 75, 175)
sender.addPolygonPoint(ele, 50, 150)
#self.sender.addPolygonPoint(ele, 200, 150)
#self.sender.addPolygonPoint(ele, 200, 150)

#self.sender.newCursor(self.warpedSurf[2], 512/2, 512/2)
window = sender.newWindow(3, 200, 200, 100, 100, "Bob")
sender.newTexRectangle(window, 200, 400, 300, 400, "van_gough.jpg")
sender.newRectangle(window, 50, 400, 100, 200, (1,1,1,1), (0.5,0.3,0.5,1))
sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 100, 30, "Arial", (1,1,0,1))
sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 200, 30, "Arial", (1,1,0,1))
sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 300, 30, "Arial", (1,1,0,1))
sender.newText(window, "Goodbye polygon  | nogylop eybdooG", 30, 400, 30, "Arial", (1,1,0,1))

#self.sender.newCursor(self.warpedSurf[3], 512/2, 512/2)
window = sender.newWindow(4, 200, 200, 100, 100, "Bob")
sender.newTexRectangle(window, 200, 400, 300, 400, "the_scream.jpg")
sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 100, 30, "Arial", (1,1,0,1))
sender.newLine(window, 0, 0, 512, 512, (0,1,1,1), 2)
sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 200, 30, "Arial", (1,1,0,1))
sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 300, 30, "Arial", (1,1,0,1))
sender.newText(window, "Goodbye rectangle  | elgnatcer eybdooG", 30, 400, 30, "Arial", (1,1,0,1))

while(1):
    time.sleep(1.0/30)
    pos = sender.getCirclePosition(blueCirc)
    if(pos[0]>=512):
        dirleft = False
    if(pos[0]<=0):
        dirleft = True
    if(dirleft):
        sender.relocateCircle(blueCirc, pos[0]+5, pos[1], window)
    else:
        sender.relocateCircle(blueCirc, pos[0]-5, pos[1], window)