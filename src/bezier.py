import math

class bezierCalc:
    
    def oppControl(self, point, control):
        return (float(point[0])+(float(point[0])-float(control[0])),float(point[1])+(float(point[1])-float(control[1])))
    
    def calculateBezierPoint(self,points,controlPoints,t):
        t = round(t,2)
        point = self.calculateBezierSubPoint(t%1, points[int(math.floor(t))], controlPoints[int(math.floor(t))], self.oppControl(points[int(math.ceil(t))],controlPoints[int(math.ceil(t))]), points[int(math.ceil(t))])
        return point
        
    def calculateBezierSubPoint(self,t,p1,p1_direct,p2_direct,p2):
        u = 1-t
        tpow2 = t*t
        upow2 = u*u
        upow3 = upow2 * u
        tpow3 = tpow2 * t
        
        px = upow3 * float(p1[0])
        px = px + (3 * upow2 * t * p1_direct[0])
        px = px + (3 * u * tpow2 * p2_direct[0])
        px = px + (tpow3 * float(p2[0]))
        
        py = upow3 * float(p1[1])
        py = py + (3 * upow2 * t * p1_direct[1])
        py = py + (3 * u * tpow2 * p2_direct[1])
        py = py + (tpow3 * float(p2[1]))
        
        return(px,py)
    
    def getSubCurvePoints(self,num_points, p1, p1_direct, p2_direct, p2):
        points = []
        for i in range(0,num_points+1):
            t = i / float(num_points)
            point = self.calculateBezierSubPoint(t, p1, p1_direct, p2_direct, p2)
            points.append(point)
        return points
    
    def getCurvePoints(self,points,controlPoints,num):
        end = len(points)-1
        x = 0
        diff = float(end)/num
        finalPoints = []
        while(round(x,3)<=end):
            #print(x)
            finalPoints.append(self.calculateBezierPoint(points, controlPoints, x))
            x+=diff
        return finalPoints