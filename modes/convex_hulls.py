#!/usr/bin/env python3

import numpy as np
from timeit import default_timer as timer

from modes import points_lines as pl


class ConvexHulls():
    def __init__(self, parent):
        self.parent = parent
        self.algorithm = 0  # 0 - Jarvis, 1 - Graham, 2 - Quickhull
        self.points = np.array([])

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def set_points(self, points):
        self.points = np.array(points, dtype=float)

    def calculate(self):
        if self.algorithm == 0:
            return jarvis_march(self.points, self.parent)
        elif self.algorithm == 1:
            graham_scan(self.points)
        elif self.algorithm == 2:
            quickhull(self.points)

        return np.array([[50, 50], [100, 100]])


def almost_equal(a, b):
    return np.abs(a - b) < 0.000001


def jarvis_march(points, main):
    start_extreme = timer()

    # Find extreme point (start of convex hull)
    points = points[np.lexsort((points[:, 0], points[:, 1]))]
    e = points[0]

    end_extreme = timer()

    # main.plot_point(e, text="E", color="blue")  # Debug

    start_first = timer()

    # Find second point by calculating angles to all points (smallest angle)
    min_angle, min_i = np.inf, -1
    for i, p in enumerate(points[1:]):
        angle = np.arctan2(p[1] - e[1], p[0] - e[0])
        if angle < min_angle:
            min_angle, min_i = angle, i + 1
        elif almost_equal(angle, min_angle):
            # Take smaller distance if same angles
            if pl.euclidean_dist(e, p) < pl.euclidean_dist(e, points[min_i]):
                min_angle, min_i = angle, i + 1

    end_first = timer()

    ch_points = np.vstack((e, points[min_i]))
    points = np.delete(points, (min_i), axis=0)

    start_other = timer()

    # Find all other points
    pi = ch_points[-1]
    while not np.array_equal(pi, e):
        min_angle, min_i = np.inf, -1
        for i, p in enumerate(points):
            a = pi - ch_points[-2]  # Vector from previous point to last point
            b = p - pi  # Vector from last point to new point
            angle = np.arctan2(b[1], b[0]) - np.arctan2(a[1], a[0])
            if angle < 0:
                angle += 2 * np.pi  # Bring into positive

            if angle < min_angle:
                min_angle, min_i = angle, i
            elif almost_equal(angle, min_angle):
                # Take smaller distance if same angles
                if pl.euclidean_dist(pi, p) < pl.euclidean_dist(pi, points[min_i]):
                    min_angle, min_i = angle, i

        ch_points = np.vstack((ch_points, points[min_i]))
        points = np.delete(points, (min_i), axis=0)
        pi = ch_points[-1]

    end_other = timer()

    time_extreme = (end_extreme - start_extreme) * 1000
    time_first = (end_first - start_first) * 1000
    time_other = (end_other - start_other) * 1000
    main.log("Calculated convex hull using Jarvis March algorithm in {} ms:"
             .format(int(time_extreme + time_first + time_other)))
    main.log("- Found extreme point in {} ms".format(int(time_extreme)))
    main.log("- Found second point using extreme in {} ms".format(int(time_first)))
    main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points


def graham_scan(points):
    return 0


def quickhull(points):
    return 0
