from messageSender import *

sender = messageSender()

sender.loadDefinedSurfaces("DEFAULT")
cur = sender.newCursor(0, 0.5, 0.5, "prop")
list = {}
for x in range(1,5):
    win = sender.newCanvas(x, 0, 1, 1, 1,"prop", "mywin")
    list[x] = win
    sender.newRectangle(win, 0, 1, 1, 1, "prop", (1,0,0,1), 10, (0,0,1,1))
    sender.newCircle(win, 0.5, 0.5, 0.25, "prop", (1,1,1,1), 10, (1,1,1,1), 10)
for x in range(1, 5):
    sender.newTexRectangle(list[x], 0.5, 1, 0.5, 0.5, "prop", "checks.jpg")
lTor = True
tTob = True
surfaceWidth = sender.getSurfacePixelWidth(0)
surfaceHeight = sender.getSurfacePixelWidth(0)
while (True):
    if lTor == True:
        if tTob == True:
            sender.shiftCursor(cur, 5, -3)
        else:
            sender.shiftCursor(cur, 5, 3)
    else:
        if tTob == True:
            sender.shiftCursor(cur, -5, -3)
        else:
            sender.shiftCursor(cur, -5, 3)
    loc = sender.getCursorPosition(cur)
    if float(loc[0]) < 0:
        lTor = True
    elif float(loc[0]) > surfaceWidth:
        lTor = False
    if float(loc[1]) < 0:
        tTob = False
    elif float(loc[1]) > surfaceHeight:
        tTob = True