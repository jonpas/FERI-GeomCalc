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

    def get_point_indexes(self, p):
        indexes = []
        for i, point in enumerate([self.p1, self.p2, self.p3, self.p4]):
            if np.array_equal(p, point):
                indexes.append(i)
        return indexes

    # Returns tuple of (number)result and (string)text
    def calculate(self):
        if self.mode == 0:
            distance = euclidean_dist(self.p1, self.p2)
            text = "Euclidean distance between P1 and P2:\n{:g}".format(distance)
            return distance, text, None, None, None
        elif self.mode == 1:
            falls_on, pp, distance, closest = orth_projection(self.p1, self.p2, self.p3)

            closest_text = "PP"
            text = "Orthogonal projection of P1 onto L1(P2,P3):\nPP ({:g}, {:g})".format(pp[0], pp[1])
            if not falls_on:
                text += ", but does not fall on the line."
                closest_text = "P2" if np.array_equal(closest, self.p2) else "P3"
            text += "\nShortest distance to line is between P1 and {}: {:g}".format(closest_text, distance)

            return distance, text, pp, closest, "PP"
        elif self.mode == 2:
            pi, itype = intersection(self.p1, self.p2, self.p3, self.p4)

            if itype == "coincident":
                text = "Coincident on L1(P1,P2) and L2(P3,P4) between:\n"

                equal = np.array_equal(self.p1, self.p3) and np.array_equal(self.p2, self.p4)
                equal_inv = np.array_equal(self.p1, self.p4) and np.array_equal(self.p2, self.p3)
                if equal or equal_inv:
                    # Full coincident
                    text += "P1/P3 ({:g}, {:g}) and P2/P4 ({:g}, {:g})".format(
                            self.p1[0], self.p1[1], self.p2[0], self.p2[1])
                else:
                    # Partial coincident (sort by x, then by y)
                    points = np.array([self.p1, self.p2, self.p3, self.p4])
                    p1, p2 = points[np.lexsort((points[:, 0], points[:, 1]))][1:-1]

                    # Find equal points (for pretty output only)
                    eq_p1 = self.get_point_indexes(p1)[0]
                    eq_p2 = self.get_point_indexes(p2)[0]

                    text += "P{} ({:g}, {:g}) and P{} ({:g}, {:g})".format(
                            eq_p1 + 1, p1[0], p1[1],
                            eq_p2 + 1, p2[0], p2[1])

                return 0, text, p1, p2, "line"

            if itype == "touch":
                text = "L1(P1,P2) and L2(P3,P4) touch at:\nPI ({:g}, {:g})".format(
                       pi[0], pi[1])

                # Find equal points (for pretty output only)
                eq_points = self.get_point_indexes(pi)
                for eq_p in eq_points:
                    text += " = P{}".format(eq_p + 1)

                return 0, text, pi, None, "PI"

            if itype == "intersection":
                text = "Intersection between L1(P1,P2) and L2(P3,P4):\n"
                text += "PI ({:g}, {:g})".format(pi[0], pi[1])

                return 0, text, pi, None, "PI"

            if itype == "parallel":
                text = "L1(P1,P2) and L2(P3,P4) are parallel."
            else:
                text = "Nothing common between L1(P1,P2) and L2(P3,P4)."

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

    if d == 0:
        # Lines coincide
        if a == b == 0:
            return None, "coincident"

        # Lines are parallel
        return None, "parallel"

    ua = a / d
    ub = b / d

    # Lines do not touch
    if not 0 <= ua <= 1 and not 0 <= ub <= 1:
        return None, "none"

    # Calculate touching point
    x = p1[0] + ua * (p2[0] - p1[0])
    y = p1[1] + ua * (p2[1] - p1[1])
    xy = np.array([x, y])

    if ua == 0 or ua == 1 or ub == 0 or ub == 1:
        return xy, "touch"
    else:
        return xy, "intersection"
