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
            distance = euclidean_dist(self.p1, self.p2)
            text = "Euclidean distance between P1 and P2:\n{:g}".format(distance)
            return distance, text, None, None, None
        elif self.mode == 1:
            falls_on, pp, distance, closest = orth_projection(self.p1, self.p2, self.p3)

            closest_text = "PP"
            text = "Orthogonal projection of P1 onto L1(P2,P3):\nP5 ({:g}, {:g})".format(pp[0], pp[1])
            if not falls_on:
                text += ", but does not fall on the line."
                closest_text = "P2" if np.array_equal(closest, self.p2) else "P3"
            text += "\nClosest distance to line is between P1 and {}: {:g}".format(closest_text, distance)

            return distance, text, pp, closest, "PP"
        elif self.mode == 2:
            pi, itype = intersection(self.p1, self.p2, self.p3, self.p4)

            text = "Intersection between L1(P1,P2) and L2(P3,P4):\n"
            if itype == "coincide":
                text += "Coincident between\nP1/P3 ({:g}, {:g}) and P2/P4 ({:g}, {:g})".format(
                    self.p1[0], self.p1[1], self.p2[0], self.p2[1])
                return 0, text, self.p1, self.p2, "line"

            if itype == "intersection":
                text += "PI ({:g}, {:g})".format(pi[0], pi[1])
                eq_p1 = "P1" if np.array_equal(pi, self.p1) else ""
                eq_p1 = "P2" if np.array_equal(pi, self.p2) else eq_p1
                eq_p2 = "P3" if np.array_equal(pi, self.p3) else ""
                eq_p2 = "P4" if np.array_equal(pi, self.p4) else eq_p2
                if eq_p1:
                    text += " = {}".format(eq_p1)
                if eq_p2:
                    text += " = {}".format(eq_p2)
                return 0, text, pi, None, "PI"

            text += "None"
            if itype == "parallel":
                text += ", lines are parallel."
            return 0, text, None, None, ""


def euclidean_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def orth_projection(p1, p2, p3):
    v1 = p3 - p2  # Vector P2 to P3
    v2 = p1 - p2  # Vector P2 to P1

    if np.any(v1):
        vN = v1 / np.linalg.norm(v1)  # Base vector, specifying new X axis
    else:
        vN = v1

    sp = np.dot(vN, v2)
    pp = p2 + vN * sp  # Projected point

    falls_on = 0 <= sp <= np.linalg.norm(v1)  # Does projection fall on the line
    closest = pp  # Closest point to line
    if falls_on:
        distance = euclidean_dist(p1, pp)  # Distance between P1 and PP
    else:
        # Find closest
        distance_p2 = euclidean_dist(p1, p2)
        distance_p3 = euclidean_dist(p1, p3)

        distance = distance_p2  # Distance between P1 and closest end-point of line
        closest = p2

        if distance_p3 < distance_p2:
            distance = distance_p3
            closest = p3

    # Projection falls on line, projected point, closest distance to line, closest point on line
    return falls_on, pp, distance, closest


def intersection(p1, p2, p3, p4):
    d = np.cross(p2 - p1, p4 - p3)
    a = np.cross(p4 - p3, p1 - p3)
    b = np.cross(p2 - p1, p1 - p3)

    # Lines coincide
    if d == a == b == 0:
        return None, "coincide"

    if d == 0:
        return None, "parallel"

    ua = a / d
    ub = b / d

    if not 0 <= ua <= 1 and not 0 <= ub <= 1:
        return None, "none"

    x = p1[0] + ua * (p2[0] - p1[0])
    y = p1[1] + ua * (p2[1] - p1[1])

    return np.array([x, y]), "intersection"
