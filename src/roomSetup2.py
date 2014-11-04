from Tkinter import *
from messageSender import *
import pygame
import threading
import time
from pygame.locals import *
from math import *
from bezier import *
from ConfigParser import SafeConfigParser
import datetime
from pgu import gui
import tkMessageBox

class client:
	__slots__ = ['ppe']
	cornerdrag = False
	quit = False
	topCircles = {}
	bottomCircles = {}
	leftCircles = {}
	rightCircles = {}
	topbz = {}
	bottombz = {}
	leftbz = {}
	rightbz = {}
	symbolicDrag = {}
	rightDragging = []
	dragging = []
	hideable = []
	orientation = {}
	mirrored = {}
	warpedSurf = {}
	bezierUpdates = {} #[top,bottom,left,right]
	centerPoints = {}
	setuplines = True
	refreshrate = 0
	connections = []
	dontFlip = {}
	sideToCorners = {"top" : ("tl", "tr"), "bottom" : ("bl", "br"), "left" : ("tl", "bl"), "right" : ("tr", "br")}
	cursorMode = "default"
	
	cornerAdj = {"tl": (("tr","top"), ("bl","left")), "tr": (("tl","top"), ("br","right")), "br": (("bl","bottom"), ("tr","right")), "bl": (("br","bottom"), ("tl","left"))}
	
	#Scan for beziers that need to be updated and call them to be updated when appropriate
	def bezierUpdateTracker(self):
		while(self.quit==False):
			for x in range(0,len(self.bezierUpdates)):
				try:
					if (self.bezierUpdates[x][0]==True):
						self.updateBezier("top",x)
						self.bezierUpdates[x][0] = False
					if (self.bezierUpdates[x][1]==True):
						self.updateBezier("bottom",x)
						self.bezierUpdates[x][1] = False
					if(self.bezierUpdates[x][2] == True):
						self.updateBezier("left",x)
						self.bezierUpdates[x][2] = False
					if(self.bezierUpdates[x][3] == True):
						self.updateBezier("right",x)
						self.bezierUpdates[x][3] = False
				except:
					pass
			time.sleep(0.0/30)
			
	def lineIntersection(self, x1a, y1a, x2a, y2a, x1b, y1b, x2b, y2b):
		dx = x2a - x1a
		dy = y2a - y1a
		m1 = dy / dx
		c1 = y1a - m1 * x1a
		
		dx = x2b - x1b
		dy = y2b - y1b
		m2 = dy / dx
		c2 = y1b - m2 * x1b
		
		if((m1 - m2) == 0):
			print "No Intersection"
			return None
		else:
			intersection_X = (c2-c1) / (m1 - m2)
			intersection_Y = m1 * intersection_X + c1
			return (intersection_X, intersection_Y)
	
	#Get the midpoint between two points
	def getMidPoints(self, point1, point2):
		return ((float(point1[0])+float(point2[0]))/float(2), (float(point1[1])+float(point2[1]))/float(2))
	
	#Get the opposite curve control point by mirroring the point over the control point
	def oppControl(self, point, control):
		return (float(point[0])+(float(point[0])-float(control[0])),float(point[1])+(float(point[1])-float(control[1])))
	
	#Halves the number of waypoints on the curve
	def reduceSide(self, circles, side, surface):
		if(len(circles)>3):
			count = (len(circles)-1)/2
			for x in list(reversed(range(0,count))):
				circle = circles[2*x+1]
				circles.pop(2*x+1)
				self.sender.removeElement(circle, 1)
			if(side == "top"):
				self.bezierUpdates[surface][0] = True
			elif(side == "bottom"):
				self.bezierUpdates[surface][1] = True
			elif(side == "left"):
				self.bezierUpdates[surface][2] = True
			elif(side == "right"):
				self.bezierUpdates[surface][3] = True
	
	#Doubles the number of waypoints on the curve
	def splitSide(self, circles, side, surface):
		count = len(circles)
		if(count<17): #Restrict to a maximum of 15 waypoints per side
			insert = []
			for x in range(1, count):
				point1 = self.sender.getCirclePosition(circles[x-1])
				point2 = self.sender.getCirclePosition(circles[x])
				midpoint = self.getMidPoints((point1[0],point1[1]), (point2[0],point2[1])) 
				insert.append(midpoint)
			for x in reversed(range(0,len(insert))):
				ele = self.sender.newCircle(1, insert[x][0], int(insert[x][1]), 7, (1, 0, 0, 1), (0, 1, 0, 1), 20)
				self.hideable.append(ele)
				circles.insert(x+1, ele)
			if(side == "top"):
				self.bezierUpdates[surface][0] = True
			elif(side == "bottom"):
				self.bezierUpdates[surface][1] = True
			elif(side == "left"):
				self.bezierUpdates[surface][2] = True
			elif(side == "right"):
				self.bezierUpdates[surface][3] = True
			
	#Rebuilds the bezier curve for the requested surface side
	def updateBezier(self, side, surface):
		points = []
		circles = []
		if(side=="top"):
			circles = self.topCircles[surface]
		elif(side=="bottom"):
			circles = self.bottomCircles[surface]
		elif(side=="left"):
			circles = self.leftCircles[surface]
		elif(side=="right"):
			circles = self.rightCircles[surface]
		for x in range(0,len(circles)):
			pos = self.sender.getCirclePosition(circles[x])
			points.append((pos[0],pos[1]))
		calc = bezierCalc()
		if(side=="top"):
			curve = calc.getCurvePoints(points, self.ppe)
			self.sender.setLineStripContent(self.topbz[surface],curve)
			self.connectionUpdateCheck(surface, "tl")
			self.connectionUpdateCheck(surface, "tr")
		elif(side=="bottom"):
			curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
			self.sender.setLineStripContent(self.bottombz[surface],curve)
			self.connectionUpdateCheck(surface, "bl")
			self.connectionUpdateCheck(surface, "br")
		elif(side=="left"):
			curve = calc.getCurvePoints(list(reversed(points)), self.ppe)
			self.sender.setLineStripContent(self.leftbz[surface],curve)
			self.connectionUpdateCheck(surface, "tl")
			self.connectionUpdateCheck(surface, "bl")
		elif(side=="right"):
			curve = calc.getCurvePoints(points, self.ppe)
			self.sender.setLineStripContent(self.rightbz[surface],curve)
			self.connectionUpdateCheck(surface, "tr")
			self.connectionUpdateCheck(surface, "br")
	
	#Tells you whether a click is within 10 pixels of a point		
	def isHit(self, point1, point2, radius):
		a = abs(float(point1[0])-float(point2[0]))
		b = abs(float(point1[1])-float(point2[1]))
		csq = pow(a,2) + pow(b,2)
		c = sqrt(csq)
		if (c<float(radius)):
			return True
		else:
			return False
		
	#Gathers the curve points for the requested surface and passes them to the server so that the mesh can be updated
	def updateMesh(self, surface):
		topPoints = []
		for x in range(0,len(self.topCircles[surface])):
			topPoints.append(self.sender.getCirclePosition(self.topCircles[surface][x]))
		bottomPoints = []
		for x in range(0,len(self.bottomCircles[surface])):
			bottomPoints.append(self.sender.getCirclePosition(self.bottomCircles[surface][len(self.bottomCircles[surface]) - 1 - x]))
		leftPoints = []
		for x in range(0,len(self.leftCircles[surface])):
			leftPoints.append(self.sender.getCirclePosition(self.leftCircles[surface][x]))
		rightPoints = []
		for x in range(0,len(self.rightCircles[surface])):
			rightPoints.append(self.sender.getCirclePosition(self.rightCircles[surface][len(self.rightCircles[surface]) - 1 - x]))
		self.sender.setSurfaceEdges(self.warpedSurf[surface], topPoints, bottomPoints, leftPoints, rightPoints)
		
	#Creates a visible line to indicate a connection between two corners of different surfaces or removes it if it exists. If appropriate sides are connected
	def createConnectionLine(self, start, end, visOnly):
		found = False
		for x in range(0,len(self.connections)):
			if(found==False):
				if (start[0]==self.connections[x][0][0] and start[1]==self.connections[x][0][1] and end[0]==self.connections[x][1][0] and end[1]==self.connections[x][1][1]):
					found = True
					self.sender.removeElement(self.connections[x][2], 1)
					self.connections.pop(x)
				elif (end[0]==self.connections[x][0][0] and end[1]==self.connections[x][0][1] and start[0]==self.connections[x][1][0] and start[1]==self.connections[x][1][1]):
					found = True
					self.sender.removeElement(self.connections[x][2], 1)
					self.connections.pop(x)
		if(found==False):
			startLoc = None
			if(start[1]=="tl"):
				startLoc = self.sender.getCirclePosition(self.topCircles[start[0]][0])
			elif(start[1]=="tr"):
				topend = len(self.topCircles[start[0]])-1
				startLoc = self.sender.getCirclePosition(self.topCircles[start[0]][topend])
			elif(start[1]=="br"):
				startLoc = self.sender.getCirclePosition(self.bottomCircles[start[0]][0])
			elif(start[1]=="bl"):
				botend = len(self.bottomCircles[start[0]])-1
				startLoc = self.sender.getCirclePosition(self.bottomCircles[start[0]][botend])
			endLoc = None
			if(end[1]=="tl"):
				endLoc = self.sender.getCirclePosition(self.topCircles[end[0]][0])
			elif(end[1]=="tr"):
				topend = len(self.topCircles[end[0]])-1
				endLoc = self.sender.getCirclePosition(self.topCircles[end[0]][topend])
			elif(end[1]=="br"):
				endLoc = self.sender.getCirclePosition(self.bottomCircles[end[0]][0])
			elif(end[1]=="bl"):
				botend = len(self.bottomCircles[end[0]])-1
				endLoc = self.sender.getCirclePosition(self.bottomCircles[end[0]][botend])
			ele = self.sender.newLine(1, startLoc[0], startLoc[1], endLoc[0], endLoc[1], (1,0,0,1), 3)
			self.connections.append([(start[0],start[1]),(end[0],end[1]),ele])
		if(not visOnly):
			#look for created connections
			for x in range(len(self.connections)):
				if(self.connections[x][0][0]==start[0] and self.connections[x][0][1]==self.cornerAdj[start[1]][0][0]):
					if(self.connections[x][1][0]==end[0] and self.connections[x][1][1]==self.cornerAdj[end[1]][0][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][0][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][0][1])
					if(self.connections[x][1][0]==end[0] and self.connections[x][1][1]==self.cornerAdj[end[1]][1][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][1][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][1][1])
				elif(self.connections[x][1][0]==start[0] and self.connections[x][1][1]==self.cornerAdj[start[1]][0][0]):
					if(self.connections[x][0][0]==end[0] and self.connections[x][0][1]==self.cornerAdj[end[1]][0][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][0][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][0][1])
					if(self.connections[x][0][0]==end[0] and self.connections[x][0][1]==self.cornerAdj[end[1]][1][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][1][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][0][1], end[0], self.cornerAdj[end[1]][1][1])
				if(self.connections[x][0][0]==start[0] and self.connections[x][0][1]==self.cornerAdj[start[1]][1][0]):
					if(self.connections[x][1][0]==end[0] and self.connections[x][1][1]==self.cornerAdj[end[1]][0][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][0][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][0][1])
					if(self.connections[x][1][0]==end[0] and self.connections[x][1][1]==self.cornerAdj[end[1]][1][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][1][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][1][1])
				elif(self.connections[x][1][0]==start[0] and self.connections[x][1][1]==self.cornerAdj[start[1]][1][0]):
					if(self.connections[x][0][0]==end[0] and self.connections[x][0][1]==self.cornerAdj[end[1]][0][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][0][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][0][1])
					if(self.connections[x][0][0]==end[0] and self.connections[x][0][1]==self.cornerAdj[end[1]][1][0]):
						if(found==False):
							self.sender.connectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][1][1])
						else:
							self.sender.disconnectSurfaces(start[0], self.cornerAdj[start[1]][1][1], end[0], self.cornerAdj[end[1]][1][1])
			
	#Checks whether a point movement should alter an existing visualised connection line
	def connectionUpdateCheck(self, surface, corner):
		for x in range(len(self.connections)):
			if(self.connections[x][0][0]==surface and self.connections[x][0][1]==corner or self.connections[x][1][0]==surface and self.connections[x][1][1]==corner):
				startLoc = None
				if(self.connections[x][0][1]=="tl"):
					startLoc = self.sender.getCirclePosition(self.topCircles[self.connections[x][0][0]][0])
				elif(self.connections[x][0][1]=="tr"):
					topend = len(self.topCircles[self.connections[x][0][0]])-1
					startLoc = self.sender.getCirclePosition(self.topCircles[self.connections[x][0][0]][topend])
				elif(self.connections[x][0][1]=="br"):
					startLoc = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][0][0]][0])
				elif(self.connections[x][0][1]=="bl"):
					botend = len(self.bottomCircles[self.connections[x][0][0]])-1
					startLoc = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][0][0]][botend])
				endLoc = None
				if(self.connections[x][1][1]=="tl"):
					endLoc = self.sender.getCirclePosition(self.topCircles[self.connections[x][1][0]][0])
				elif(self.connections[x][1][1]=="tr"):
					topend = len(self.topCircles[self.connections[x][1][0]])-1
					endLoc = self.sender.getCirclePosition(self.topCircles[self.connections[x][1][0]][topend])
				elif(self.connections[x][1][1]=="br"):
					endLoc = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][1][0]][0])
				elif(self.connections[x][1][1]=="bl"):
					botend = len(self.bottomCircles[self.connections[x][1][0]])-1
					endLoc = self.sender.getCirclePosition(self.bottomCircles[self.connections[x][1][0]][botend])
				self.sender.setLineStart(self.connections[x][2], startLoc[0], startLoc[1])
				self.sender.setLineEnd(self.connections[x][2], endLoc[0], endLoc[1])

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
						self.sender.rotateCursorClockwise(1,10) #Tells the server to rotate the cursor clockwise
					#Runs if the mouse wheel is being rolled downwards
					elif event.button==5:
						self.sender.rotateCursorAnticlockwise(1,10) #Tells the server to rotate the cursor anticlockwise
					#Runs if the middle mouse button is pressed
					elif event.button==2:
						self.mClickTime=datetime.datetime.now() #Saves the current time so that when the button is released click duration can be checked
					#Runs if the right mouse button is pressed
					elif event.button==3:
						self.rClickTime=datetime.datetime.now() #Saves the current time so that when the button is released click duration can be checked
						#Runs if the default cursor mode is active
						if(self.cursorMode=="default"):
							loc = self.sender.getCursorPosition(1)
							self.rightDragging = []
							#Checks whether a corner point has been clicked and if so starts defining a connection
							for z in range(0,len(self.topCircles)):
								hit = False
								point = self.sender.getCirclePosition(self.topCircles[z][0])
								radius = self.sender.getCircleRadius(self.topCircles[z][0])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
									self.rightDragging.append((self.topCircles[z][0],"tl",z))
									hit = True
								end = len(self.topCircles[z])-1
								point = self.sender.getCirclePosition(self.topCircles[z][end])
								radius = self.sender.getCircleRadius(self.topCircles[z][end])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
									self.rightDragging.append((self.topCircles[z][end],"tr",z))
									hit = True
								point = self.sender.getCirclePosition(self.bottomCircles[z][0])
								radius = self.sender.getCircleRadius(self.bottomCircles[z][0])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
									self.rightDragging.append((self.bottomCircles[z][0],"br",z))
									hit = True
								end = len(self.bottomCircles[z])-1
								point = self.sender.getCirclePosition(self.bottomCircles[z][end])
								radius = self.sender.getCircleRadius(self.bottomCircles[z][end])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
									self.rightDragging.append((self.bottomCircles[z][end],"bl",z))
									hit = True
								if(hit==True):
									cirpos = self.sender.getCirclePosition(self.rightDragging[0][0])
									self.symbolicDrag[0] = self.sender.newLine(1, cirpos[0], cirpos[1], loc[0], loc[1], (1, 0, 0, 1), 3)
									self.symbolicDrag[1] = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 0, 0, 1), 20)
					elif event.button==1:
						self.lClickTime=datetime.datetime.now() #Saves the current time so that when the button is released click duration can be checked
						#If the user is trying to create a corner point it is defined then returned
						if(get_point==True):
							loc = self.sender.getCursorPosition(1)
							ele = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
							self.hideable.append(ele)
							return (loc, ele)
						#If the user isn't trying to create a corner point it is checked whether they have clicked on an existing point so it can be dragged
						else:
							#Runs if the default cursor mode is active
							if(self.cursorMode=="default"):
								loc = self.sender.getCursorPosition(1)
								self.dragging = []
								self.cornerdrag = False
								for z in range(0,len(self.topCircles)):
									for x in range(0,len(self.topCircles[z])):
										point = self.sender.getCirclePosition(self.topCircles[z][x])
										radius = self.sender.getCircleRadius(self.topCircles[z][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.dragging.append(self.topCircles[z][x])
											if (x == 0 or x == (len(self.topCircles[z])-1)):
												self.cornerdrag = True
									for x in range(0,len(self.bottomCircles[z])):
										point = self.sender.getCirclePosition(self.bottomCircles[z][x])
										radius = self.sender.getCircleRadius(self.bottomCircles[z][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.dragging.append(self.bottomCircles[z][x])
											if (x == 0 or x == (len(self.bottomCircles[z])-1)):
												self.cornerdrag = True
									for x in range(0,len(self.leftCircles[z])):
										point = self.sender.getCirclePosition(self.leftCircles[z][x])
										radius = self.sender.getCircleRadius(self.leftCircles[z][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.dragging.append(self.leftCircles[z][x])
											if (x == 0 or x == (len(self.leftCircles[z])-1)):
												self.cornerdrag = True
									for x in range(0,len(self.rightCircles[z])):
										point = self.sender.getCirclePosition(self.rightCircles[z][x])
										radius = self.sender.getCircleRadius(self.rightCircles[z][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.dragging.append(self.rightCircles[z][x])
											if (x == 0 or x == (len(self.rightCircles[z])-1)):
												self.cornerdrag = True
				elif event.type == pygame.MOUSEBUTTONUP:
					#Runs if the left mouse button has been released
					if(event.button==1):
						lClickRelTime=datetime.datetime.now()
						elapsedSecs = (lClickRelTime-self.lClickTime).total_seconds() #Checks how long the button was depressed
						#Runs if the button was pressed for less than 0.15 seconds
						if(elapsedSecs<0.15):
							#Runs if the default cursor mode is active
							if(self.cursorMode=="default"):
								loc = self.sender.getCursorPosition(1)
								for w in range(0,len(self.topCircles)):
									#If a waypoint has been clicked, the side it was part of is split so that there are twice as many waypoints
									for x in range(1,len(self.topCircles[w])-1):
										point = self.sender.getCirclePosition(self.topCircles[w][x])
										radius = self.sender.getCircleRadius(self.topCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.splitSide(self.topCircles[w], "top",w)
											self.updateMesh(w)
									for x in range(1,len(self.bottomCircles[w])-1):
										point = self.sender.getCirclePosition(self.bottomCircles[w][x])
										radius = self.sender.getCircleRadius(self.bottomCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.splitSide(self.bottomCircles[w], "bottom",w)
											self.updateMesh(w)
									for x in range(1,len(self.leftCircles[w])-1):
										point = self.sender.getCirclePosition(self.leftCircles[w][x])
										radius = self.sender.getCircleRadius(self.leftCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.splitSide(self.leftCircles[w], "left",w)
											self.updateMesh(w)
									for x in range(1,len(self.rightCircles[w])-1):
										point = self.sender.getCirclePosition(self.rightCircles[w][x])
										radius = self.sender.getCircleRadius(self.rightCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											self.splitSide(self.rightCircles[w], "right",w)
											self.updateMesh(w)
									#If a corner point has been clicked, the surface is mirrored or rotated as appropriate
									if (get_point!=True):
										if(self.dontFlip[w]==False):
											flipped = False
											point = self.sender.getCirclePosition(self.topCircles[w][0])
											radius = self.sender.getCircleRadius(self.topCircles[w][0])
											if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
												if(self.orientation[w]!=0):
													if(self.mirrored[w]==False):
														self.sender.rotateSurfaceTo0(w+1)
													else:
														self.sender.rotateSurfaceTo270(w+1)
													self.orientation[w]=0
												else:
													if(self.mirrored[w]==False):
														self.sender.rotateSurfaceTo270(w+1)
														self.sender.mirrorSurface(w+1)
														self.mirrored[w]=True
													else:
														self.sender.rotateSurfaceTo0(w+1)
														self.sender.mirrorSurface(w+1)
														self.mirrored[w]=False
												flipped = True
											if(flipped == False):
												point = self.sender.getCirclePosition(self.topCircles[w][len(self.topCircles[w])-1])
												radius = self.sender.getCircleRadius(self.topCircles[w][len(self.topCircles[w])-1])
												if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
													if(self.orientation[w]!=1):
														if(self.mirrored[w]==False):
															self.sender.rotateSurfaceTo90(w+1)
														else:
															self.sender.rotateSurfaceTo0(w+1)
														self.orientation[w]=1
													else:
														if(self.mirrored[w]==False):
															self.sender.rotateSurfaceTo0(w+1)
															self.sender.mirrorSurface(w+1)
															self.mirrored[w]=True
														else:
															self.sender.rotateSurfaceTo90(w+1)
															self.sender.mirrorSurface(w+1)
															self.mirrored[w]=False
													flipped = True
											if (flipped == False):
												point = self.sender.getCirclePosition(self.bottomCircles[w][0])
												radius = self.sender.getCircleRadius(self.bottomCircles[w][0])
												if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
													if(self.orientation[w]!=2):
														if(self.mirrored[w]==False):
															self.sender.rotateSurfaceTo180(w+1)
														else:
															self.sender.rotateSurfaceTo90(w+1)
														self.orientation[w]=2
													else:
														if(self.mirrored[w]==False):
															self.sender.rotateSurfaceTo90(w+1)
															self.sender.mirrorSurface(w+1)
															self.mirrored[w]=True
														else:
															self.sender.rotateSurfaceTo180(w+1)
															self.sender.mirrorSurface(w+1)
															self.mirrored[w]=False
													flipped = True
											if (flipped==False):
												point = self.sender.getCirclePosition(self.bottomCircles[w][len(self.bottomCircles[w])-1])
												radius = self.sender.getCircleRadius(self.bottomCircles[w][len(self.bottomCircles[w])-1])
												if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
													if(self.orientation[w]!=3):
														if(self.mirrored[w]==False):
															self.sender.rotateSurfaceTo270(w+1)
														else:
															self.sender.rotateSurfaceTo180(w+1)
														self.orientation[w]=3
													else:
														if(self.mirrored[w]==False):
															self.sender.rotateSurfaceTo180(w+1)
															self.sender.mirrorSurface(w+1)
															self.mirrored[w]=True
														else:
															self.sender.rotateSurfaceTo270(w+1)
															self.sender.mirrorSurface(w+1)
															self.mirrored[w]=False
										else:
											self.dontFlip[w]=False
						#If appropriate the list of points currently being dragged is cleared
						for w in range(0,len(self.topCircles)):
							if (len(self.topCircles[w])>1 and len(self.bottomCircles[w])>1 and len(self.leftCircles[w])>1 and len(self.rightCircles[w])>1):
								self.dragging=[]
								self.updateMesh(w)
					#Runs if the middle mouse button has been released
					if(event.button==2):
						mClickRelTime=datetime.datetime.now()
						elapsedSecs = (mClickRelTime-self.mClickTime).total_seconds() #Checks how long the button was depressed
						#Runs if the button was pressed for less than 0.25 seconds and unlocks the mouse from the server
						if(elapsedSecs<0.25):
							self.mouseLock = False
							pygame.mouse.set_visible(True)
							self.master.focus_force()
					#Runs if the right mouse button has been released
					if(event.button==3):
						rClickRelTime=datetime.datetime.now()
						elapsedSecs = (rClickRelTime-self.rClickTime).total_seconds() #Checks how long the button was depressed
						hit = False
						hitOnce = False
						#Runs if the button was pressed for less than 0.15 seconds
						if(elapsedSecs<0.15):
							#Runs if the default cursor mode is active
							if(self.cursorMode=="default"):
								loc = self.sender.getCursorPosition(1)
								#If a waypoint has been clicked, the number of waypoints on the side is halved
								for w in range(0,len(self.topCircles)):
									for x in range(1,len(self.topCircles[w])-1):
										point = self.sender.getCirclePosition(self.topCircles[w][x])
										radius = self.sender.getCircleRadius(self.topCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											hit = True
											hitOnce = True
									if (hit==True):
										hit=False
										self.reduceSide(self.topCircles[w], "top",w)
										self.updateMesh(w)
									for x in range(1,len(self.bottomCircles[w])-1):
										point = self.sender.getCirclePosition(self.bottomCircles[w][x])
										radius = self.sender.getCircleRadius(self.bottomCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											hit = True
											hitOnce = True
									if (hit==True):
										hit=False
										self.reduceSide(self.bottomCircles[w], "bottom",w)
										self.updateMesh(w)
									for x in range(1,len(self.leftCircles[w])-1):
										point = self.sender.getCirclePosition(self.leftCircles[w][x])
										radius = self.sender.getCircleRadius(self.leftCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											hit = True
											hitOnce = True
									if (hit==True):
										hit=False
										self.reduceSide(self.leftCircles[w], "left",w)
										self.updateMesh(w)
									for x in range(1,len(self.rightCircles[w])-1):
										point = self.sender.getCirclePosition(self.rightCircles[w][x])
										radius = self.sender.getCircleRadius(self.rightCircles[w][x])
										if(self.isHit((point[0],point[1]),(loc[0],loc[1]),radius)):
											hit = True
											hitOnce = True
									if (hit==True):
										hit=False
										self.reduceSide(self.rightCircles[w], "right",w)
										self.updateMesh(w)
						dropPoint = None
						#The temporary connection line is deleted after its current end point is recorded
						if(len(self.symbolicDrag)>0):
							dropPoint = self.sender.getCirclePosition(self.symbolicDrag[1])
							self.sender.removeElement(self.symbolicDrag[0], 1)
							self.sender.removeElement(self.symbolicDrag[1], 1)
						#The list of items that were being dragged is scanned
						for rDragInd in range(0,len(self.rightDragging)):
							temp = self.rightDragging[rDragInd]
							loc = self.sender.getCirclePosition(temp[0])
							corner = temp[1]
							surface = temp[2]
							#If the dragged point was released over another point a connection line is created
							for w in range(0,len(self.topCircles)):
								if (w != surface):
									point = self.sender.getCirclePosition(self.topCircles[w][0])
									radius = self.sender.getCircleRadius(self.topCircles[w][0])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]),radius)):
										self.createConnectionLine((surface,corner),(w,"tl"), False)
									end = len(self.topCircles[w])-1
									point = self.sender.getCirclePosition(self.topCircles[w][end])
									radius = self.sender.getCircleRadius(self.topCircles[w][end])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]),radius)):
										self.createConnectionLine((surface,corner),(w,"tr"), False)
									point = self.sender.getCirclePosition(self.bottomCircles[w][0])
									radius = self.sender.getCircleRadius(self.bottomCircles[w][0])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]),radius)):
										self.createConnectionLine((surface,corner),(w,"br"), False)
									end = len(self.bottomCircles[w])-1
									point = self.sender.getCirclePosition(self.bottomCircles[w][end])
									radius = self.sender.getCircleRadius(self.bottomCircles[w][end])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]),radius)):
										self.createConnectionLine((surface,corner),(w,"bl"), False)
						self.rightDragging=[]
						self.symbolicDrag = {}
						#Runs if the button was pressed for less than 0.25 seconds and a point wasn't hit
						if(elapsedSecs<0.25 and hitOnce==False):
							#Runs if the default cursor mode is active
							if(self.cursorMode=="default"):
								#Switches to wall defining mode and begins definition if there are less than 4 walls, otherwise switches to screen defining mode
								if(self.surfaceCounter<4):
									self.sender.setCursorWallMode(1)
									self.cursorMode="wall"
									self.defineSurface()
									if(self.sender.getCursorMode(1)=="wall"):
										self.splitSide(self.topCircles[self.surfaceCounter-1], "top",self.surfaceCounter-1)
										self.splitSide(self.bottomCircles[self.surfaceCounter-1], "bottom",self.surfaceCounter-1)
										self.splitSide(self.leftCircles[self.surfaceCounter-1], "left",self.surfaceCounter-1)
										self.splitSide(self.rightCircles[self.surfaceCounter-1], "right",self.surfaceCounter-1)
										self.sender.setCursorDefaultMode(1)
										self.cursorMode="default"
								else:
									self.sender.setCursorScreenMode(1)
									self.cursorMode="screen"
							#Runs if the wall defining cursor mode is active and switches to the screen defining mode
							elif(self.cursorMode=="wall"):
								self.sender.setCursorScreenMode(1)
								self.cursorMode="screen"
							#Runs if the screen defining cursor mode is active and switches to the blocked area defining mode
							elif(self.cursorMode=="screen"):
								self.sender.setCursorBlockMode(1)
								self.cursorMode="block"
							#Runs if the blocked area defining cursor mode is active and switches to the default defining mode
							elif(self.cursorMode=="block"):
								self.sender.setCursorDefaultMode(1)
								self.cursorMode="default"
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
					
					self.sender.moveCursor(1, -xdist, ydist)
					self.sender.moveCursor(2, -xdist, ydist)
					loc = self.sender.getCursorPosition(1)
					if(len(self.dragging)!=0):
						for x in range (0,len(self.dragging)):
							self.sender.relocateCircle(self.dragging[x], float(loc[0]), float(loc[1]), 1)
							for y in range(0,len(self.bezierUpdates)):
								try:
									if(self.topCircles[y].__contains__(self.dragging[x])):
										self.bezierUpdates[y][0] = True
										if(self.cornerdrag == True):
											tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
											trcoor = self.sender.getCirclePosition(self.topCircles[y][len(self.topCircles[y])-1])
											brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
											blcoor = self.sender.getCirclePosition(self.bottomCircles[y][len(self.bottomCircles[y])-1])
											center = self.lineIntersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1], trcoor[0], trcoor[1], blcoor[0], blcoor[1])
											self.sender.relocateCircle(self.centerPoints[y], center[0], center[1], 1)
									if(self.bottomCircles[y].__contains__(self.dragging[x])):
										self.bezierUpdates[y][1] = True
										if(self.cornerdrag == True):
											tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
											trcoor = self.sender.getCirclePosition(self.topCircles[y][len(self.topCircles[y])-1])
											brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
											blcoor = self.sender.getCirclePosition(self.bottomCircles[y][len(self.bottomCircles[y])-1])
											center = self.lineIntersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1], trcoor[0], trcoor[1], blcoor[0], blcoor[1])
											self.sender.relocateCircle(self.centerPoints[y], center[0], center[1], 1)
									if(self.leftCircles[y].__contains__(self.dragging[x])):
										self.bezierUpdates[y][2] = True
										if(self.cornerdrag == True):
											tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
											trcoor = self.sender.getCirclePosition(self.topCircles[y][len(self.topCircles[y])-1])
											brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
											blcoor = self.sender.getCirclePosition(self.bottomCircles[y][len(self.bottomCircles[y])-1])
											center = self.lineIntersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1], trcoor[0], trcoor[1], blcoor[0], blcoor[1])
											self.sender.relocateCircle(self.centerPoints[y], center[0], center[1], 1)
									if(self.rightCircles[y].__contains__(self.dragging[x])):
										self.bezierUpdates[y][3] = True
										if(self.cornerdrag == True):
											tlcoor = self.sender.getCirclePosition(self.topCircles[y][0])
											trcoor = self.sender.getCirclePosition(self.topCircles[y][len(self.topCircles[y])-1])
											brcoor = self.sender.getCirclePosition(self.bottomCircles[y][0])
											blcoor = self.sender.getCirclePosition(self.bottomCircles[y][len(self.bottomCircles[y])-1])
											center = self.lineIntersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1], trcoor[0], trcoor[1], blcoor[0], blcoor[1])
											self.sender.relocateCircle(self.centerPoints[y], center[0], center[1], 1)
								except:
									pass
					if(len(self.rightDragging)!=0):
						try:
							self.sender.relocateCircle(self.symbolicDrag[1], float(loc[0]), float(loc[1]), 1)
							self.sender.setLineEnd(self.symbolicDrag[0], float(loc[0]), float(loc[1]))
						except:
							pass
			
	#Defines all required surfaces according to a layout data structure				
	def redefineSurface(self,layout):
		for x in range(0,len(layout)):
			self.orientation[self.surfaceCounter]=0
			self.mirrored[self.surfaceCounter]=False
			
			self.topCircles[self.surfaceCounter] = []
			self.bottomCircles[self.surfaceCounter] = []
			self.leftCircles[self.surfaceCounter] = []
			self.rightCircles[self.surfaceCounter] = []
			self.bezierUpdates[self.surfaceCounter] = [False,False,False,False]
			
			y=0
			for z in range(0,len(layout[x][y])):
				if(z==0):
					self.topbz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (0,0.75,0,1), 5)
				else:
					self.sender.addLineStripPoint(self.topbz[self.surfaceCounter], layout[x][y][z][0], layout[x][y][z][1])
				ele = None
				if ((z==0) or (z==(len(layout[x][y])-1))):
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
				else:
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, (1, 0, 0, 1), (0, 1, 0, 1), 20)
				self.topCircles[self.surfaceCounter].append(ele)
			y=1
			for z in list(reversed(range(0,len(layout[x][y])))):
				if(z==len(layout[x][y])-1):
					self.bottombz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (0,0.75,0,1), 5)
				else:
					self.sender.addLineStripPoint(self.bottombz[self.surfaceCounter], layout[x][y][z][0], layout[x][y][z][1])
				ele = None
				if ((z==0) or (z==(len(layout[x][y])-1))):
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
				else:
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, (1, 0, 0, 1), (0, 1, 0, 1), 20)
				self.bottomCircles[self.surfaceCounter].append(ele)
			y=2
			for z in range(0,len(layout[x][y])):
				if(z==0):
					self.leftbz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (0,0.75,0,1), 5)
				else:
					self.sender.addLineStripPoint(self.leftbz[self.surfaceCounter], layout[x][y][z][0], layout[x][y][z][1])
				ele = None
				if ((z==0) or (z==(len(layout[x][y])-1))):
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
				else:
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, (1, 0, 0, 1), (0, 1, 0, 1), 20)
				self.leftCircles[self.surfaceCounter].append(ele)
			y=3
			for z in list(reversed(range(0,len(layout[x][y])))):
				if(z==len(layout[x][y])-1):
					self.rightbz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (0,0.75,0,1), 5)
				else:
					self.sender.addLineStripPoint(self.rightbz[self.surfaceCounter], layout[x][y][z][0], layout[x][y][z][1])
				ele = None
				if ((z==0) or (z==(len(layout[x][y])-1))):
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
				else:
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, (1, 0, 0, 1), (0, 1, 0, 1), 20)
				self.rightCircles[self.surfaceCounter].append(ele)
			self.bezierUpdates[self.surfaceCounter] = [True,True,True,True]
			tlcoor = self.sender.getCirclePosition(self.topCircles[self.surfaceCounter][0])
			trcoor = self.sender.getCirclePosition(self.topCircles[self.surfaceCounter][len(self.topCircles[self.surfaceCounter])-1])
			brcoor = self.sender.getCirclePosition(self.bottomCircles[self.surfaceCounter][0])
			blcoor = self.sender.getCirclePosition(self.bottomCircles[self.surfaceCounter][len(self.bottomCircles[self.surfaceCounter])-1])
			center = self.lineIntersection(tlcoor[0], tlcoor[1], brcoor[0], brcoor[1], trcoor[0], trcoor[1], blcoor[0], blcoor[1])
			self.centerPoints[self.surfaceCounter] = self.sender.newCircle(1, center[0], center[1], 10, (0,0,0,1), (1,0,1,1), 20)
			self.surfaceCounter+=1
			self.dontFlip[self.surfaceCounter-1] = True
	
	#Allows the user to define the four corners of a surface
	def defineSurface(self):
		self.orientation[self.surfaceCounter]=0
		self.mirrored[self.surfaceCounter]=False
		tl = None
		bl = None
		tr = None
		br = None
		
		self.topCircles[self.surfaceCounter] = []
		self.bottomCircles[self.surfaceCounter] = []
		self.leftCircles[self.surfaceCounter] = []
		self.rightCircles[self.surfaceCounter] = []
		self.bezierUpdates[self.surfaceCounter] = [False,False,False,False]
		
		while(self.quit==False and tl==None and self.cursorMode=="wall"):
			self.background.fill((255, 255, 255))
			text = self.font.render("Click the top left", 1, (10, 10, 10))
			textpos = text.get_rect()
			textpos.centerx = self.background.get_rect().centerx
			self.background.blit(text, textpos)
			tl = self.getInput(True)
			self.screen.blit(self.background, (0, 0))
			pygame.display.flip()
		if(self.quit==False and self.cursorMode=="wall"):
			self.topCircles[self.surfaceCounter].append(tl[1])
			self.topbz[self.surfaceCounter] = self.sender.newLineStrip(1, tl[0][0], tl[0][1], (0,0.75,0,1), 5)
			self.hideable.append(self.topbz[self.surfaceCounter])
			
		while(self.quit==False and tr==None) and self.cursorMode=="wall":
			self.background.fill((255, 255, 255))
			text = self.font.render("Click the top right", 1, (10, 10, 10))
			textpos = text.get_rect()
			textpos.centerx = self.background.get_rect().centerx
			self.background.blit(text, textpos)
			tr = self.getInput(True)
			self.screen.blit(self.background, (0, 0))
			pygame.display.flip()
		if(self.quit==False and self.cursorMode=="wall"):
			self.topCircles[self.surfaceCounter].append(tr[1])
			self.sender.addLineStripPoint(self.topbz[self.surfaceCounter], tr[0][0], tr[0][1])
			self.rightCircles[self.surfaceCounter].append(tr[1])
			self.rightbz[self.surfaceCounter] = self.sender.newLineStrip(1, tr[0][0], tr[0][1], (0,0.75,0,1), 5)
			self.hideable.append(self.rightbz[self.surfaceCounter])
			
		while(self.quit==False and br==None and self.cursorMode=="wall"):
			self.background.fill((255, 255, 255))
			text = self.font.render("Click the bottom right", 1, (10, 10, 10))
			textpos = text.get_rect()
			textpos.centerx = self.background.get_rect().centerx
			self.background.blit(text, textpos)
			br = self.getInput(True)
			self.screen.blit(self.background, (0, 0))
			pygame.display.flip()
		if(self.quit==False and self.cursorMode=="wall"):
			self.rightCircles[self.surfaceCounter].append(br[1])
			self.sender.addLineStripPoint(self.rightbz[self.surfaceCounter], br[0][0], br[0][1])
			self.bottomCircles[self.surfaceCounter].append(br[1])
			self.bottombz[self.surfaceCounter] = self.sender.newLineStrip(1, br[0][0], br[0][1], (0,0.75,0,1), 5)
			self.hideable.append(self.bottombz[self.surfaceCounter])
			
		while(self.quit==False and bl==None and self.cursorMode=="wall"):
			self.background.fill((255, 255, 255))
			text = self.font.render("Click the bottom left", 1, (10, 10, 10))
			textpos = text.get_rect()
			textpos.centerx = self.background.get_rect().centerx
			self.background.blit(text, textpos)
			bl = self.getInput(True)
			self.screen.blit(self.background, (0, 0))
			pygame.display.flip()
		if(self.quit==False and self.cursorMode=="wall"):
			self.bottomCircles[self.surfaceCounter].append(bl[1])
			self.sender.addLineStripPoint(self.bottombz[self.surfaceCounter], bl[0][0], bl[0][1])
			self.leftCircles[self.surfaceCounter].append(bl[1])
			self.leftbz[self.surfaceCounter] = self.sender.newLineStrip(1, bl[0][0], bl[0][1], (0,0.75,0,1), 5)
			self.hideable.append(self.leftbz[self.surfaceCounter])
			self.leftCircles[self.surfaceCounter].append(tl[1])
			self.sender.addLineStripPoint(self.leftbz[self.surfaceCounter], tl[0][0], tl[0][1])
			center = self.lineIntersection(tl[0][0], tl[0][1], br[0][0], br[0][1], tr[0][0], tr[0][1], bl[0][0], bl[0][1])
			self.centerPoints[self.surfaceCounter] = self.sender.newCircle(1, center[0], center[1], 10, (0,0,0,1), (1,0,1,1), 20)
			self.surfaceCounter += 1
			self.dontFlip[self.surfaceCounter-1] = True
		if(self.cursorMode!="wall"):
			self.orientation.pop(self.surfaceCounter)
			self.mirrored.pop(self.surfaceCounter)
			tl = None
			bl = None
			tr = None
			br = None
			try:
				self.sender.removeElement(self.topbz[self.surfaceCounter], 1)
				self.topbz.pop(self.surfaceCounter)
			except:
				pass
			try:
				self.sender.removeElement(self.bottombz[self.surfaceCounter], 1)
				self.bottombz.pop(self.surfaceCounter)
			except:
				pass
			try:
				self.sender.removeElement(self.leftbz[self.surfaceCounter], 1)
				self.leftbz.pop(self.surfaceCounter)
			except:
				pass
			try:
				self.sender.removeElement(self.rightbz[self.surfaceCounter], 1)
				self.rightbz.pop(self.surfaceCounter)
			except:
				pass
			for x in range(0,len(self.topCircles[self.surfaceCounter])):
				self.sender.removeElement(self.topCircles[self.surfaceCounter][x], 1)
			self.topCircles.pop(self.surfaceCounter)
			for x in range(0,len(self.bottomCircles[self.surfaceCounter])):
				self.sender.removeElement(self.bottomCircles[self.surfaceCounter][x], 1)
			self.bottomCircles.pop(self.surfaceCounter)
			for x in range(0,len(self.leftCircles[self.surfaceCounter])):
				self.sender.removeElement(self.leftCircles[self.surfaceCounter][x], 1)
			self.leftCircles.pop(self.surfaceCounter)
			for x in range(0,len(self.rightCircles[self.surfaceCounter])):
				self.sender.removeElement(self.rightCircles[self.surfaceCounter][x], 1)
			self.rightCircles.pop(self.surfaceCounter)
			self.bezierUpdates.pop(self.surfaceCounter)
			
	#looks through a data structure holding connections and draws connection lines as appropriate
	def visualizeConnections(self, connections):
		for x in range(0, len(connections)):
			self.visualizeConnectionLines((connections[x][0][0],connections[x][0][1]), (connections[x][1][0],connections[x][1][1]))
	
	#Creates both connection lines which indicate a connection between the two defined surface sides
	def visualizeConnectionLines(self, fromSide, toSide):
		self.createConnectionLine((fromSide[0],self.sideToCorners[fromSide[1]][0]), (toSide[0],self.sideToCorners[toSide[1]][0]), True)
		self.createConnectionLine((fromSide[0],self.sideToCorners[fromSide[1]][1]), (toSide[0],self.sideToCorners[toSide[1]][1]), True)
	
	#Quits the client
	def quitButton(self):
		if(self.quit==False):
			self.quit=True
			time.sleep(0.2)
			self.frame.quit()
	
	#Quits the client and server
	def quitAllButton(self):
		if(self.quit==False):
			self.sender.quit()
			time.sleep(0.1)
			self.quit=True
			time.sleep(0.2)
			self.frame.quit()
	
	#Locks the mouse so that the server can be controlled
	def LockMouse(self):
		self.mouseLock = True
		pygame.mouse.set_visible(False)
	
	#Requests for the existing layout to be saved to a file
	def saveLayout(self):
		if(self.saveName.get()!=""):
			hit=False
			confirm = False
			for x in range(0,self.loadList.size()):
				if(self.loadList.get(x)==self.saveName.get()):
					hit=True
			if hit==True:
				confirm = tkMessageBox.askyesno("Overwrite", "Overwrite existing \"" + self.saveName.get() + "\" layout?")
			if hit==False or confirm==True:
				self.sender.saveDefinedSurfaces(self.saveName.get())
				self.layouts = self.sender.getSavedLayouts()
				self.loadList.delete(0, END)
				for x in range(0, len(self.layouts)):
					self.loadList.insert(END, self.layouts[x])
		else:
			tkMessageBox.showinfo("Error", "Please enter save name first")
	
	#Requests for the currently selected layout to be loaded
	def loadLayout(self):
		self.clearLayout()
		count = self.sender.loadDefinedSurfaces(self.loadList.selection_get())
		self.redefineSurface(count[1])
		self.visualizeConnections(count[2])
		self.saveName.delete(0, END)
		self.saveName.insert(0, self.loadList.selection_get())
	
	#Makes it so that the save filename matches the current selection in the layout list
	def selectEntry(self, event):
		w = event.widget
		index = int(w.curselection()[0])
		value = w.get(index)
		self.saveName.delete(0, END)
		self.saveName.insert(0, value)
	
	#Refreshes the layout list by querying the server for an updated list
	def refreshLayouts(self):
		self.layouts = self.sender.getSavedLayouts()
		self.loadList.delete(0, END)
		for x in range(0, len(self.layouts)):
			self.loadList.insert(END, self.layouts[x])
	
	#Ask the server to delete the layout that is currently selected in the layout list
	def deleteLayout(self):
		if(self.loadList.selection_get()!="DEFAULT"):
			self.sender.deleteLayout(self.loadList.selection_get())
			self.layouts = self.sender.getSavedLayouts()
			self.loadList.delete(0, END)
			for x in range(0, len(self.layouts)):
				self.loadList.insert(END, self.layouts[x])
		else:
			tkMessageBox.showinfo("Error", "You are not allowed to delete the \"DEFAULT\" layout")
	
	#Clear the currently defined layout on both the client and server side
	def clearLayout(self):
		self.sender.undefineSurface(self.warpedSurf[0])
		self.sender.undefineSurface(self.warpedSurf[1])
		self.sender.undefineSurface(self.warpedSurf[2])
		self.sender.undefineSurface(self.warpedSurf[3])
		for z in self.topCircles:
			for x in range(0,len(self.topCircles[z])):
				self.sender.removeElement(self.topCircles[z][x], 1)
		self.topCircles = {}
		for z in self.bottomCircles:
			for x in range(0,len(self.bottomCircles[z])):
				self.sender.removeElement(self.bottomCircles[z][x], 1)
		self.bottomCircles = {}
		for z in self.leftCircles:
			for x in range(0,len(self.leftCircles[z])):
				self.sender.removeElement(self.leftCircles[z][x], 1)
		self.leftCircles = {}
		for z in self.rightCircles:
			for x in range(0,len(self.rightCircles[z])):
				self.sender.removeElement(self.rightCircles[z][x], 1)
		self.rightCircles = {}
		for x in self.topbz:
			self.sender.removeElement(self.topbz[x], 1)
		self.topbz = {}
		for x in self.bottombz:
			self.sender.removeElement(self.bottombz[x], 1)
		self.bottombz = {}
		for x in self.leftbz:
			self.sender.removeElement(self.leftbz[x], 1)
		self.leftbz = {}
		for x in self.rightbz:
			self.sender.removeElement(self.rightbz[x], 1)
		self.rightbz = {}
		for x in self.mirrored:
			self.mirrored[x] = False
		for x in self.orientation:
			self.orientation[x] = 0
		
		self.surfaceCounter = 0
		
		self.saveName.delete(0, END)
		self.saveName.insert(0, "")
	
	#Defines the GUI
	def tkinthread(self):
		self.master = Tk()
		self.master.wm_title("Configuration GUI")
		self.frame = Frame(self.master)
		self.frame.pack()
		self.frame2 = Frame(self.master)
		self.frame2.pack()
		self.frame3 = Frame(self.master)
		self.frame3.pack()
		self.frame4 = Frame(self.master)
		self.frame4.pack()
		self.frame5 = Frame(self.master)
		self.frame5.pack()
		self.frame6 = Frame(self.master)
		self.frame6.pack()
		self.frame7 = Frame(self.master)
		self.frame7.pack()
		self.button = Button(self.frame, text="QUIT CLIENT AND SERVER", fg="red", command=self.quitAllButton, width=40)
		self.button.pack(side=LEFT)
		self.slogan = Button(self.frame2, text="Control Projected Mouse (Middle Click to Release)", command=self.LockMouse, width=40)
		self.slogan.pack(side=LEFT)
		self.label = Label(self.frame3, text="Save name", width=10)
		self.label.pack(side=LEFT)
		self.saveName = Entry(self.frame3, width=32)
		self.saveName.pack(side=LEFT)
		self.saveBut = Button(self.frame4, text="Save Layout", command=self.saveLayout, width=40)
		self.saveBut.pack(side=LEFT)
		self.loadList = Listbox(self.frame5, width=42)
		self.loadList.pack(side=LEFT)
		time.sleep(0.5)
		index = 0
		for x in range(0, len(self.layouts)):
			if self.layouts[x]=="DEFAULT":
				index = x
			self.loadList.insert(END, self.layouts[x])
		self.loadList.bind('<<ListboxSelect>>', self.selectEntry)
		self.saveBut = Button(self.frame6, text="Load Layout", command=self.loadLayout, width=18)
		self.saveBut.pack(side=LEFT)
		self.saveBut = Button(self.frame6, text="Refresh List", command=self.refreshLayouts, width=18)
		self.saveBut.pack(side=LEFT)
		self.saveBut = Button(self.frame7, text="Delete Layout", command=self.deleteLayout, width=18)
		self.saveBut.pack(side=LEFT)
		self.saveBut = Button(self.frame7, text="Clear Current Layout", command=self.clearLayout, width=18)
		self.saveBut.pack(side=LEFT)
		self.loadList.select_set(index)
		self.loadLayout()
		self.master.mainloop()
	
	#Sets up the surfaces which can be defined within the client
	def initGUI(self):
		self.sender.showSetupSurface()
		self.sender.newWindow(0, 0, 1024, 1280, 1024, "setupWindow")
		self.sender.newCursor(0, 1280/2, 1024/2)
		
		self.warpedSurf[0] = self.sender.newSurface()
		self.window = self.sender.newWindow(self.warpedSurf[0], 200, 200, 100, 100, "Bob")
		self.sender.newCursor(self.warpedSurf[0], 512/2, 512/2)
		self.sender.newTexRectangle(self.window, 0, 512, 512, 512, "checks.jpg")

		self.warpedSurf[1] = self.sender.newSurface()
		self.window = self.sender.newWindow(self.warpedSurf[1], 200, 200, 100, 100, "Bob")
		self.sender.newTexRectangle(self.window, 0, 512, 512, 512, "checks.jpg")

		self.warpedSurf[2] = self.sender.newSurface()
		self.window = self.sender.newWindow(self.warpedSurf[2], 200, 200, 100, 100, "Bob")
		self.sender.newTexRectangle(self.window, 0, 512, 512, 512, "checks.jpg")

		self.warpedSurf[3] = self.sender.newSurface()
		self.window = self.sender.newWindow(self.warpedSurf[3], 200, 200, 100, 100, "Bob")
		self.sender.newTexRectangle(self.window, 0, 512, 512, 512, "checks.jpg")
		
		self.surfaceCounter = 0

	#The main loop
	def __init__(self):
		tkinterThread = threading.Thread(target=self.tkinthread, args=()) #Creates the display thread
		tkinterThread.start() #Starts the display thread
		
		parser = SafeConfigParser()
		parser.read("config.ini")
		self.ppe = parser.getint('RoomSetup','PointsPerEdge')
		self.refreshrate = 1/(parser.getint('library','MovesPerSecond'))
		self.sender = messageSender()
		self.winWidth = 320
		self.winHeight = 240
		
		# Initialise screen
		pygame.init()
		self.screen = pygame.display.set_mode((self.winWidth, self.winHeight))
		pygame.display.set_caption('Room setup program')
	
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
		
		self.sender.login("jp438")
		self.sender.setapp("myapp")
		self.layouts = self.sender.getSavedLayouts()
		self.initGUI()
		
		self.mouseLock=False
		pygame.mouse.set_visible(True)
		
		mouseThread = threading.Thread(target=self.mouseMovement, args=()) #Creates the display thread
		mouseThread.start() #Starts the display thread
		
		if(self.quit==False):
			thread = threading.Thread(target=self.bezierUpdateTracker, args=()) #Creates the display thread
			thread.start() #Starts the display thread
			self.dirleft = True
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