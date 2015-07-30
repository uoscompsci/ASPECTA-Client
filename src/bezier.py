import math


class BezierCalc:
    @staticmethod
    def get_midpoints(point1, point2):
        return (float(point1[0]) + float(point2[0])) / float(2), (float(point1[1]) + float(point2[1])) / float(2)

    @staticmethod
    def opposite_control_point(point, control):
        return (float(point[0]) + (float(point[0]) - float(control[0])),
                float(point[1]) + (float(point[1]) - float(control[1])))

    def get_control_points(self, points):
        control_points = [self.get_midpoints((points[0][0], points[0][1]), (points[1][0], points[1][1]))]
        for x in range(1, len(points)):
            control_points.append(self.opposite_control_point((points[x][0], points[x][1]), control_points[x - 1]))
        for x in range(0, len(control_points)):
            control_points[x] = self.find_third(points[x], control_points[x])
        return control_points

    @staticmethod
    def find_third(point1, point2):
        xdiff = float(point2[0] - point1[0])
        ydiff = float(point2[1] - point1[1])
        csq = pow(xdiff, 2) + pow(ydiff, 2)
        c = math.sqrt(csq)
        xdiff /= c
        ydiff /= c
        xdiff *= c / 3 * 2
        ydiff *= c / 3 * 2
        return point1[0] + xdiff, point1[1] + ydiff

    def calculateBezierPoint(self, points, control_points, t):
        t = round(t, 2)
        point = self.calculateBezierSubPoint(t % 1, points[int(math.floor(t))], control_points[int(math.floor(t))],
                                             self.opposite_control_point(points[int(math.ceil(t))],
                                             control_points[int(math.ceil(t))]),
                                             points[int(math.ceil(t))])
        return point

    def calculateBezierSubPoint(self, t, p1, p1_direct, p2_direct, p2):
        u = 1 - t
        tpow2 = t * t
        upow2 = u * u
        upow3 = upow2 * u
        tpow3 = tpow2 * t

        px = upow3 * float(p1[0])
        px += 3 * upow2 * t * p1_direct[0]
        px += 3 * u * tpow2 * p2_direct[0]
        px += tpow3 * float(p2[0])

        py = upow3 * float(p1[1])
        py += 3 * upow2 * t * p1_direct[1]
        py += 3 * u * tpow2 * p2_direct[1]
        py += tpow3 * float(p2[1])

        return px, py

    def getSubCurvePoints(self, num_points, p1, p1_direct, p2_direct, p2):
        points = []
        for i in range(0, num_points + 1):
            t = i / float(num_points)
            point = self.calculateBezierSubPoint(t, p1, p1_direct, p2_direct, p2)
            points.append(point)
        return points

    def getCurvePoints(self, points, num):
        control_points = self.get_control_points(points)
        end = len(points) - 1
        x = 0
        diff = float(end) / num
        final_points = []
        while round(x, 3) <= end:
            final_points.append(self.calculateBezierPoint(points, control_points, x))
            x += diff
        return final_points
