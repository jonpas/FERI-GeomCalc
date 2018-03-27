#!/usr/bin/env python3

import math
import numpy as np


class PointsLines():
    def __init__(self):
        self.mode = 0  # 0 - 1 point, 1 - 1 point 1 line, 2 - 2 lines
        self.p1, self.p2, self.p3, self.p4 = [np.zeros(2)] * 4

    def set_mode(self, mode):
        self.mode = mode

    def set_points(self, points):
        points = np.array(points, dtype=float)
        self.p1, self.p2, self.p3, self.p4 = points

    # Returns tuple of (numer)result and (string)text
    def calculate(self):
        if self.mode == 0:
            distance = self.euclidean_dist(self.p1, self.p2)
            text = "Euclidean distance between P1 and P2:\n{}".format(distance)
            return distance, text, None, None
        elif self.mode == 1:
            exists, p5, distance, closest = self.orth_projection(self.p1, self.p2, self.p3)

            text = "Orthogonal projection of P1 onto L1(P2,P3):\n"
            if exists:
                text += "P5 ({}, {})\n".format(p5[0], p5[1])
                text += "Distance between P1 and P5: {}".format(distance)
            else:
                text += "P5 does not exist\n"
                closest = "P2" if np.array_equal(p5, self.p2) else "P3"
                text += "Shortest distance is between P1 and {}: {}".format(closest, distance)

            return distance, text, p5, closest
        elif self.mode == 2:
            result = self.intersection(self.p1, self.p2, self.p3, self.p4)
            return result, "Intersection between L1(P1,P2) and L2(P3,P4)\n{}".format(result), None, None

    def euclidean_dist(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def orth_projection(self, p1, p2, p3):
        v1 = p3 - p2  # Vector P2 to P3
        v2 = p1 - p2  # Vector P2 to P1

        if np.any(v1):
            vN = v1 / np.linalg.norm(v1)  # Base vector, specifying new X axis
        else:
            vN = v1

        sp = np.dot(vN, v2)
        pp = p2 + vN * sp  # Projected point

        exists = 0 <= sp <= np.linalg.norm(v1)  # Is projection even possible?
        closest = pp  # Closest point to line
        if exists:
            distance = self.euclidean_dist(p1, pp)  # Distance between P1 and PP
        else:
            # Find closest
            distance_p2 = self.euclidean_dist(p1, p2)
            distance_p3 = self.euclidean_dist(p1, p3)

            distance = distance_p2  # Distance between P1 and closest end-point of line
            closest = p2

            if distance_p3 < distance_p3:
                distance = distance_p3
                closest = p3

        # Projection exists, projected point, closest distance to line, closest point on line
        return exists, pp, distance, closest

    def intersection(self, p1, p2, p3, p4):
        print("intersection")
        return 0
