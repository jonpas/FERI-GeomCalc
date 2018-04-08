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
        print("algorithm: {}".format(self.algorithm))
        return 0
