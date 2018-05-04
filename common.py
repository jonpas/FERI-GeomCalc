#!/usr/bin/env python3

import numpy as np


# Compares 2 numbers if equal, designed for floats to overcome precision errors
def almost_equal(a, b):
    return np.abs(a - b) < 0.000001


# Faster implementation of np.cross() for 2 vectors (3 points) returning magnitude directly
def area_triangle(a, b, c):
    return area_rectangle(a, b, c, b)  # d = b


# Faster implementation of np.cross() for 2 vectors (4 points) returning magnitude directly
def area_rectangle(a, b, c, d):
    return (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
