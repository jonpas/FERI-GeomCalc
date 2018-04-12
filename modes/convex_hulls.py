#!/usr/bin/env python3

import numpy as np


class ConvexHulls():
    def __init__(self):
        self.algorithm = 0  # 0 - Jarvis, 1 - Graham, 2 - Quickhull
        self.points = np.array([])

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def set_points(self, points):
        self.points = np.array(points, dtype=float)

    def calculate(self):
        if self.algorithm == 0:
            jarvis_march()
        elif self.algorithm == 1:
            graham_scan()
        elif self.algorithm == 2:
            quickhull()
        return 0


def jarvis_march():
    return 0


def graham_scan():
    return 0


def quickhull():
    return 0
