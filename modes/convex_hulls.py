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
            return graham_scan(self.points, self.parent)
        elif self.algorithm == 2:
            return quickhull(self.points, self.parent)


def almost_equal(a, b):
    return np.abs(a - b) < 0.000001


def jarvis_march(points, main):
    start_extreme = timer()

    # Find extreme point (start of convex hull)
    points = points[np.lexsort((points[:, 0], points[:, 1]))]
    e = points[0]

    end_extreme = timer()

    # if main is not None:
    #     main.plot_point(e, text="E", color="blue")  # Debug

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

    if main is not None:
        time_extreme = (end_extreme - start_extreme) * 1000
        time_first = (end_first - start_first) * 1000
        time_other = (end_other - start_other) * 1000
        main.log("Calculated convex hull on {} points using Jarvis March algorithm in {} ms:"
                 .format(len(points), int(time_extreme + time_first + time_other)))
        main.log("- Found extreme point in {} ms".format(int(time_extreme)))
        main.log("- Found second point using extreme in {} ms".format(int(time_first)))
        main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points


def graham_scan(points, main):
    # Approximate center of gravity
    rands = np.random.choice(points.shape[0], 3, replace=False)
    o = np.mean([points[rands[0]], points[rands[1]], points[rands[2]]], axis=0)

    # if main is not None:
    #     main.plot_point(o, text="O", color="blue")  # Debug

    start_polar = timer()

    # Create polar system and sort all points based on angle
    angles = []
    for p in points:
        angle = np.arctan2(p[1] - o[1], p[0] - o[0])
        if angle < 0:
            angle += 2 * np.pi

        if angle in angles:
            i = angles.index(angle)
            if pl.euclidean_dist(o, p) < pl.euclidean_dist(o, points[i]):
                angles[i] = p
        else:
            angles.append(angle)

    angles = np.array(angles)
    points = points[angles.argsort()]

    end_polar = timer()

    start_extreme = timer()

    # Find extreme point (start of convex hull)
    e = points[np.lexsort((points[:, 0], points[:, 1]))][0]

    end_extreme = timer()

    # if main is not None:
    #     main.plot_point(e, text="E", color="blue")  # Debug

    start_other = timer()

    # Find all other points
    i = np.where(points == e)[0][0]
    p2 = None
    j = 0
    while not np.array_equal(p2, e) or j < 3:
        i1, i2, i3 = i % len(points), (i + 1) % len(points), (i + 2) % len(points)
        p1, p2, p3 = points[i1], points[i2], points[i3]
        u = np.cross(p2 - p1, p3 - p1)
        if u > 0:
            # Point p2 is part of convex hull, keep and continue
            i += 1
            j += 1
        else:
            # Point p2 is not part of convex hull, remove and return
            points = np.delete(points, (i2), axis=0)
            angles = np.delete(angles, i2)
            i -= 2
            j -= 2

    end_other = timer()

    ch_points = np.vstack((points, points[0]))

    if main is not None:
        time_polar = (end_polar - start_polar) * 1000
        time_extreme = (end_extreme - start_extreme) * 1000
        time_other = (end_other - start_other) * 1000
        main.log("Calculated convex hull on {} points using Graham Scan algorithm in {} ms:"
                 .format(len(points), int(time_polar + time_extreme + time_other)))
        main.log("- Created and sorted polar system {} ms".format(int(time_polar)))
        main.log("- Found extreme point in {} ms".format(int(time_extreme)))
        main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points


def quickhull(points, main):
    start_extreme = timer()

    # Find extreme points (start of convex hull)
    el, er = points[np.lexsort((points[:, 1], points[:, 0]))][[0, -1]]

    end_extreme = timer()

    if main is not None:
        main.plot_point(el, text="EL", color="blue")  # Debug
        main.plot_point(er, text="ER", color="blue")  # Debug

    ch_points = np.vstack((el, er))

    start_first = timer()

    # Split into 2 areas (start of recursion)

    end_first = timer()

    start_other = timer()

    # Find all other points

    end_other = timer()

    if main is not None:
        time_extreme = (end_extreme - start_extreme) * 1000
        time_first = (end_first - start_first) * 1000
        time_other = (end_other - start_other) * 1000
        main.log("Calculated convex hull on {} points using Quickhull algorithm in {} ms:"
                 .format(len(points), int(time_extreme + time_first + time_other)))
        main.log("- Found first extreme points in {} ms".format(int(time_extreme)))
        main.log("- Split first areas in {} ms".format(int(time_first)))
        main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points
