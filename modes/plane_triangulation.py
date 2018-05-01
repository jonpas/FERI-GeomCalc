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
    return np.zeros([2, 2])


def hamiltonian_path(points):
    return np.zeros([2, 2])
