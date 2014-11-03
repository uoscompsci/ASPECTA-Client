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
	setuplines = True
	refreshrate = 0
	connections = []
	dontFlip = {}
	sideToCorners = {"top" : ("tl", "tr"), "bottom" : ("bl", "br"), "left" : ("tl", "bl"), "right" : ("tr", "br")}
	cursorMode = "default"
	
	cornerAdj = {"tl": (("tr","top"), ("bl","left")), "tr": (("tl","top"), ("br","right")), "br": (("bl","bottom"), ("tr","right")), "bl": (("br","bottom"), ("tl","left"))}
	
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
	
	def getMidPoints(self, point1, point2):
		return ((float(point1[0])+float(point2[0]))/float(2), (float(point1[1])+float(point2[1]))/float(2))
	
	def oppControl(self, point, control):
		return (float(point[0])+(float(point[0])-float(control[0])),float(point[1])+(float(point[1])-float(control[1])))
	
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
			
	def isHit(self, point1, point2):
		a = abs(float(point1[0])-float(point2[0]))
		b = abs(float(point1[1])-float(point2[1]))
		csq = pow(a,2) + pow(b,2)
		c = sqrt(csq)
		if (c<10):
			return True
		else:
			return False
		
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
				elif event.key==pygame.K_SPACE:
					self.sender.saveDefinedSurfaces("spaceSave")
				elif event.key==pygame.K_v:
					if (self.setuplines == False):
						for q in range(0,len(self.hideable)):
							self.sender.hideElement(self.hideable[q])
						self.setuplines = True
					else:
						for q in range(0,len(self.hideable)):
							self.sender.showElement(self.hideable[q])
						self.setuplines = False
			if(self.mouseLock==True):
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button==4:
						self.sender.rotateCursorClockwise(1,10)
					elif event.button==5:
						self.sender.rotateCursorAnticlockwise(1,10)
					elif event.button==2:
						self.mClickTime=datetime.datetime.now()
					elif event.button==3:
						self.rClickTime=datetime.datetime.now()
						if(self.cursorMode=="default"):
							loc = self.sender.getCursorPosition(1)
							self.rightDragging = []
							for z in range(0,len(self.topCircles)):
								hit = False
								point = self.sender.getCirclePosition(self.topCircles[z][0])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
									self.rightDragging.append((self.topCircles[z][0],"tl",z))
									hit = True
								end = len(self.topCircles[z])-1
								point = self.sender.getCirclePosition(self.topCircles[z][end])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
									self.rightDragging.append((self.topCircles[z][end],"tr",z))
									hit = True
								point = self.sender.getCirclePosition(self.bottomCircles[z][0])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
									self.rightDragging.append((self.bottomCircles[z][0],"br",z))
									hit = True
								end = len(self.bottomCircles[z])-1
								point = self.sender.getCirclePosition(self.bottomCircles[z][end])
								if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
									self.rightDragging.append((self.bottomCircles[z][end],"bl",z))
									hit = True
								if(hit==True):
									cirpos = self.sender.getCirclePosition(self.rightDragging[0][0])
									self.symbolicDrag[0] = self.sender.newLine(1, cirpos[0], cirpos[1], loc[0], loc[1], (1, 0, 0, 1), 3)
									self.symbolicDrag[1] = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 0, 0, 1), 20)
					elif event.button==1:
						self.lClickTime=datetime.datetime.now()
						self.ldown=True
						if(get_point==True):
							loc = self.sender.getCursorPosition(1)
							ele = self.sender.newCircle(1, loc[0], loc[1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
							self.hideable.append(ele)
							return (loc, ele)
						if(get_point!=True):
							loc = self.sender.getCursorPosition(1)
							self.dragging = []
							for z in range(0,len(self.topCircles)):
								for x in range(0,len(self.topCircles[z])):
									point = self.sender.getCirclePosition(self.topCircles[z][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.dragging.append(self.topCircles[z][x])
								for x in range(0,len(self.bottomCircles[z])):
									point = self.sender.getCirclePosition(self.bottomCircles[z][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.dragging.append(self.bottomCircles[z][x])
								for x in range(0,len(self.leftCircles[z])):
									point = self.sender.getCirclePosition(self.leftCircles[z][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.dragging.append(self.leftCircles[z][x])
								for x in range(0,len(self.rightCircles[z])):
									point = self.sender.getCirclePosition(self.rightCircles[z][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.dragging.append(self.rightCircles[z][x])
				elif event.type == pygame.MOUSEBUTTONUP:
					if(event.button==1):
						lClickRelTime=datetime.datetime.now()
						self.ldown=False
						elapsedSecs = (lClickRelTime-self.lClickTime).total_seconds()
						if(elapsedSecs<0.15):
							loc = self.sender.getCursorPosition(1)
							for w in range(0,len(self.topCircles)):
								for x in range(1,len(self.topCircles[w])-1):
									point = self.sender.getCirclePosition(self.topCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.splitSide(self.topCircles[w], "top",w)
										self.updateMesh(w)
								for x in range(1,len(self.bottomCircles[w])-1):
									point = self.sender.getCirclePosition(self.bottomCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.splitSide(self.bottomCircles[w], "bottom",w)
										self.updateMesh(w)
								for x in range(1,len(self.leftCircles[w])-1):
									point = self.sender.getCirclePosition(self.leftCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.splitSide(self.leftCircles[w], "left",w)
										self.updateMesh(w)
								for x in range(1,len(self.rightCircles[w])-1):
									point = self.sender.getCirclePosition(self.rightCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										self.splitSide(self.rightCircles[w], "right",w)
										self.updateMesh(w)
								if (get_point!=True):
									if(self.dontFlip[w]==False):
										flipped = False
										point = self.sender.getCirclePosition(self.topCircles[w][0])
										if(self.isHit((point[0],point[1]), (loc[0],loc[1]))):
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
											if(self.isHit((point[0],point[1]), (loc[0],loc[1]))):
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
											if(self.isHit((point[0],point[1]), (loc[0],loc[1]))):
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
											if(self.isHit((point[0],point[1]), (loc[0],loc[1]))):
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
						for w in range(0,len(self.topCircles)):
							if (len(self.topCircles[w])>1 and len(self.bottomCircles[w])>1 and len(self.leftCircles[w])>1 and len(self.rightCircles[w])>1):
								self.dragging=[]
								self.updateMesh(w)
					if(event.button==2):
						mClickRelTime=datetime.datetime.now()
						self.mdown=False
						elapsedSecs = (mClickRelTime-self.mClickTime).total_seconds()
						if(elapsedSecs<0.25):
							self.mouseLock = False
							pygame.mouse.set_visible(True)
							self.master.focus_force()
					if(event.button==3):
						rClickRelTime=datetime.datetime.now()
						elapsedSecs = (rClickRelTime-self.rClickTime).total_seconds()
						hit = False
						hitOnce = False
						if(elapsedSecs<0.15):
							loc = self.sender.getCursorPosition(1)
							for w in range(0,len(self.topCircles)):
								for x in range(1,len(self.topCircles[w])-1):
									point = self.sender.getCirclePosition(self.topCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										hit = True
										hitOnce = True
								if (hit==True):
									hit=False
									self.reduceSide(self.topCircles[w], "top",w)
									self.updateMesh(w)
								for x in range(1,len(self.bottomCircles[w])-1):
									point = self.sender.getCirclePosition(self.bottomCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										hit = True
										hitOnce = True
								if (hit==True):
									hit=False
									self.reduceSide(self.bottomCircles[w], "bottom",w)
									self.updateMesh(w)
								for x in range(1,len(self.leftCircles[w])-1):
									point = self.sender.getCirclePosition(self.leftCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										hit = True
										hitOnce = True
								if (hit==True):
									hit=False
									self.reduceSide(self.leftCircles[w], "left",w)
									self.updateMesh(w)
								for x in range(1,len(self.rightCircles[w])-1):
									point = self.sender.getCirclePosition(self.rightCircles[w][x])
									if(self.isHit((point[0],point[1]),(loc[0],loc[1]))):
										hit = True
										hitOnce = True
								if (hit==True):
									hit=False
									self.reduceSide(self.rightCircles[w], "right",w)
									self.updateMesh(w)
						dropPoint = None
						if(len(self.symbolicDrag)>0):
							dropPoint = self.sender.getCirclePosition(self.symbolicDrag[1])
							self.sender.removeElement(self.symbolicDrag[0], 1)
							self.sender.removeElement(self.symbolicDrag[1], 1)
						for rDragInd in range(0,len(self.rightDragging)):
							temp = self.rightDragging[rDragInd]
							loc = self.sender.getCirclePosition(temp[0])
							corner = temp[1]
							surface = temp[2]
							for w in range(0,len(self.topCircles)):
								if (w != surface):
									point = self.sender.getCirclePosition(self.topCircles[w][0])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]))):
										self.createConnectionLine((surface,corner),(w,"tl"), False)
									end = len(self.topCircles[w])-1
									point = self.sender.getCirclePosition(self.topCircles[w][end])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]))):
										self.createConnectionLine((surface,corner),(w,"tr"), False)
									point = self.sender.getCirclePosition(self.bottomCircles[w][0])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]))):
										self.createConnectionLine((surface,corner),(w,"br"), False)
									end = len(self.bottomCircles[w])-1
									point = self.sender.getCirclePosition(self.bottomCircles[w][end])
									if(self.isHit((point[0],point[1]),(dropPoint[0],dropPoint[1]))):
										self.createConnectionLine((surface,corner),(w,"bl"), False)
						self.rightDragging=[]
						self.symbolicDrag = {}
						if(elapsedSecs<0.25 and hitOnce==False):
							if(self.cursorMode=="default"):
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
							elif(self.cursorMode=="wall"):
								self.sender.setCursorScreenMode(1)
								self.cursorMode="screen"
							elif(self.cursorMode=="screen"):
								self.sender.setCursorBlockMode(1)
								self.cursorMode="block"
							elif(self.cursorMode=="block"):
								self.sender.setCursorDefaultMode(1)
								self.cursorMode="default"
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
					
					self.sender.moveCursor(1, -xdist, ydist)
					self.sender.moveCursor(2, -xdist, ydist)
					loc = self.sender.getCursorPosition(1)
					if(len(self.dragging)!=0):
						for x in range (0,len(self.dragging)):
							self.sender.relocateCircle(self.dragging[x], float(loc[0]), float(loc[1]), 1)
							for y in range(0,len(self.bezierUpdates)):
								if(self.topCircles[y].__contains__(self.dragging[x])):
									self.bezierUpdates[y][0] = True
								if(self.bottomCircles[y].__contains__(self.dragging[x])):
									self.bezierUpdates[y][1] = True
								if(self.leftCircles[y].__contains__(self.dragging[x])):
									self.bezierUpdates[y][2] = True
								if(self.rightCircles[y].__contains__(self.dragging[x])):
									self.bezierUpdates[y][3] = True
					if(len(self.rightDragging)!=0):
						try:
							self.sender.relocateCircle(self.symbolicDrag[1], float(loc[0]), float(loc[1]), 1)
							self.sender.setLineEnd(self.symbolicDrag[0], float(loc[0]), float(loc[1]))
						except:
							print "Symbolic Drag = " + str(self.symbolicDrag)
							print "loc = " + str(loc)
							
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
					self.topbz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (1,1,1,1), 5)
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
					self.bottombz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (1,1,1,1), 5)
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
					self.leftbz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (1,1,1,1), 5)
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
					self.rightbz[self.surfaceCounter] = self.sender.newLineStrip(1, layout[x][y][z][0], layout[x][y][z][1], (1,1,1,1), 5)
				else:
					self.sender.addLineStripPoint(self.rightbz[self.surfaceCounter], layout[x][y][z][0], layout[x][y][z][1])
				ele = None
				if ((z==0) or (z==(len(layout[x][y])-1))):
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 10, (1, 0, 0, 1), (1, 1, 0, 1), 20)
				else:
					ele = self.sender.newCircle(1, layout[x][y][z][0], layout[x][y][z][1], 7, (1, 0, 0, 1), (0, 1, 0, 1), 20)
				self.rightCircles[self.surfaceCounter].append(ele)
			self.bezierUpdates[self.surfaceCounter] = [True,True,True,True]
			self.surfaceCounter+=1
			self.dontFlip[self.surfaceCounter-1] = True
	
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
			self.topbz[self.surfaceCounter] = self.sender.newLineStrip(1, tl[0][0], tl[0][1], (1,1,1,1), 5)
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
			self.rightbz[self.surfaceCounter] = self.sender.newLineStrip(1, tr[0][0], tr[0][1], (1,1,1,1), 5)
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
			self.bottombz[self.surfaceCounter] = self.sender.newLineStrip(1, br[0][0], br[0][1], (1,1,1,1), 5)
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
			self.leftbz[self.surfaceCounter] = self.sender.newLineStrip(1, bl[0][0], bl[0][1], (1,1,1,1), 5)
			self.hideable.append(self.leftbz[self.surfaceCounter])
			self.leftCircles[self.surfaceCounter].append(tl[1])
			self.sender.addLineStripPoint(self.leftbz[self.surfaceCounter], tl[0][0], tl[0][1])
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
			
	def visualizeConnections(self, connections):
		for x in range(0, len(connections)):
			self.visualizeConnectionLines((connections[x][0][0],connections[x][0][1]), (connections[x][1][0],connections[x][1][1]))
			
	def visualizeConnectionLines(self, fromSide, toSide):
		self.createConnectionLine((fromSide[0],self.sideToCorners[fromSide[1]][0]), (toSide[0],self.sideToCorners[toSide[1]][0]), True)
		self.createConnectionLine((fromSide[0],self.sideToCorners[fromSide[1]][1]), (toSide[0],self.sideToCorners[toSide[1]][1]), True)
	
	def quitButton(self):
		if(self.quit==False):
			self.quit=True
			time.sleep(0.2)
			self.frame.quit()
			
	def quitAllButton(self):
		if(self.quit==False):
			self.sender.quit()
			time.sleep(0.1)
			self.quit=True
			time.sleep(0.2)
			self.frame.quit()
	
	def LockMouse(self):
		self.mouseLock = True
		pygame.mouse.set_visible(False)
		
	def saveLayout(self):
		if(self.saveName.get()!=""):
			hit=False
			confirm = False
			for x in range(0,self.loadList.size()):
				if(self.loadList.get(x)==self.saveName.get()):
					hit=True
			if hit==True:
				confirm = tkMessageBox.askyesno("Overwrite", "Overwrite existing layout?")
			if hit==False or confirm==True:
				self.sender.saveDefinedSurfaces(self.saveName.get())
				self.layouts = self.sender.getSavedLayouts()
				self.loadList.delete(0, END)
				for x in range(0, len(self.layouts)):
					self.loadList.insert(END, self.layouts[x])
		else:
			tkMessageBox.showinfo("Error", "Please enter save name first")
		
	def loadLayout(self):
		self.clearLayout()
		count = self.sender.loadDefinedSurfaces(self.loadList.selection_get())
		self.redefineSurface(count[1])
		self.visualizeConnections(count[2])
		self.saveName.delete(0, END)
		self.saveName.insert(0, self.loadList.selection_get())
		
	def selectEntry(self, event):
		w = event.widget
		index = int(w.curselection()[0])
		value = w.get(index)
		self.saveName.delete(0, END)
		self.saveName.insert(0, value)
		
	def refreshLayouts(self):
		self.layouts = self.sender.getSavedLayouts()
		self.loadList.delete(0, END)
		for x in range(0, len(self.layouts)):
			self.loadList.insert(END, self.layouts[x])
			
	def deleteLayout(self):
		if(self.loadList.selection_get()!="DEFAULT"):
			self.sender.deleteLayout(self.loadList.selection_get())
			self.layouts = self.sender.getSavedLayouts()
			self.loadList.delete(0, END)
			for x in range(0, len(self.layouts)):
				self.loadList.insert(END, self.layouts[x])
		else:
			tkMessageBox.showinfo("Error", "Cannot delete default layout")
			
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