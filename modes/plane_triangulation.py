#!/usr/bin/env python3

import numpy as np

from modes import points_lines as pl
from modes import convex_hulls as ch


class PlaneTriangulation():
    def __init__(self, parent):
        self.parent = parent
        self.algorithm = 0  # 0 - Minimum-Weight Triangulation, 1 - Hamiltonian Path
        self.points = np.array([])

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def set_points(self, points):
        self.points = np.array(points, dtype=float)

    def calculate(self):
        if self.algorithm == 0:
            return mwt(self.points)
        elif self.algorithm == 1:
            return hamiltonian_path(self.points)


def mwt(points):
    if len(points) < 2:
        return np.array([])

    # Generate convex hull (for algorithm end check)
    hull_points = len(ch.quickhull(points)) - 1  # -1 from final connection

    # Generate all possible lines
    lines = []
    distances = []
    for i, p1 in enumerate(points):
        for p2 in points[i + 1:]:
            lines.append([p1, p2])
            distances.append(pl.euclidean_dist(p1, p2))

    # Sort lines by distance
    lines = np.array(lines)
    distances = np.array(distances)
    lines = lines[distances.argsort()]

    # Shortest line is definitely part of triangulation
    pt_lines = [lines[0]]
    lines = lines[1:]

    # Accept lines that don't intersect already accepted lines, reject others
    # Repeat until enough lines are accepted (3 * points - 3 - convex hull points)
    while len(pt_lines) < 3 * len(points) - 3 - hull_points:
        line = lines[0]

        intersection = False
        for pt_line in pt_lines:
            pi, itype = pl.intersection(line[0], line[1], pt_line[0], pt_line[1])
            if itype == "intersection":
                intersection = True
                break

        if not intersection:
            pt_lines.append(line)

        lines = lines[1:]

    return np.array(pt_lines)


def hamiltonian_path(points):
    return np.zeros([2, 2])
