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
            return jarvis_march(self.points, main=self.parent)
        elif self.algorithm == 1:
            return graham_scan(self.points, main=self.parent)
        elif self.algorithm == 2:
            return quickhull(self.points, main=self.parent)


def almost_equal(a, b):
    return np.abs(a - b) < 0.000001


# Faster implementation of np.cross() returning magnitude directly
def area_triangle(a, b, c):
    return (a[0] - b[0]) * (c[1] - b[1]) - (a[1] - b[1]) * (c[0] - b[0])


def jarvis_march(points, main=None):
    amount = len(points)

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
        if almost_equal(angle, min_angle):
            # Take smaller distance if same angles
            if pl.euclidean_dist(e, p) < pl.euclidean_dist(e, points[min_i]):
                min_angle, min_i = angle, i + 1
        elif angle < min_angle:
            min_angle, min_i = angle, i + 1

    end_first = timer()

    ch_points = np.vstack((e, points[min_i]))
    points = np.concatenate((points[:min_i], points[(min_i + 1):]))

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

            if almost_equal(angle, min_angle):
                # Take smaller distance if same angles
                if pl.euclidean_dist(pi, p) < pl.euclidean_dist(pi, points[min_i]):
                    min_angle, min_i = angle, i
            elif angle < min_angle:
                min_angle, min_i = angle, i

        ch_points = np.vstack((ch_points, points[min_i]))
        points = np.concatenate((points[:min_i], points[(min_i + 1):]))
        pi = ch_points[-1]

    end_other = timer()

    if main is not None:
        time_extreme = (end_extreme - start_extreme) * 1000
        time_first = (end_first - start_first) * 1000
        time_other = (end_other - start_other) * 1000
        main.log("Calculated convex hull on {} points using Jarvis March algorithm in {} ms:"
                 .format(amount, int(time_extreme + time_first + time_other)))
        main.log("- Found extreme point in {} ms".format(int(time_extreme)))
        main.log("- Found second point using extreme in {} ms".format(int(time_first)))
        main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points


def graham_scan(points, main=None):
    amount = len(points)

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
        angles.append(angle)

    angles = np.array(angles)
    points = points[angles.argsort()]

    end_polar = timer()

    start_extreme = timer()

    # Find extreme point (start of convex hull)
    e_i = np.lexsort((points[:, 0], points[:, 1]))[0]
    e = points[e_i]

    end_extreme = timer()

    # if main is not None:
    #     main.plot_point(e, text="E", color="blue")  # Debug

    start_other = timer()

    # Find all other points
    p2 = None
    j = 0
    while not np.array_equal(p2, e) or j < 3:
        i1, i2, i3 = e_i % len(points), (e_i + 1) % len(points), (e_i + 2) % len(points)
        p1, p2, p3 = points[i1], points[i2], points[i3]
        u = area_triangle(p2, p1, p3)
        if u > 0:
            # Point p2 is part of convex hull, keep and continue
            e_i += 1
            j += 1
        else:
            # Point p2 is not part of convex hull, remove and return
            points = np.concatenate((points[:i2], points[(i2 + 1):]))
            e_i -= 2
            j -= 2

    end_other = timer()

    ch_points = np.vstack((points, points[0]))  # Connect first and last

    if main is not None:
        time_polar = (end_polar - start_polar) * 1000
        time_extreme = (end_extreme - start_extreme) * 1000
        time_other = (end_other - start_other) * 1000
        main.log("Calculated convex hull on {} points using Graham Scan algorithm in {} ms:"
                 .format(amount, int(time_polar + time_extreme + time_other)))
        main.log("- Created and sorted polar system {} ms".format(int(time_polar)))
        main.log("- Found extreme point in {} ms".format(int(time_extreme)))
        main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points


def quickhull(points, main=None):
    amount = len(points)

    start_extreme = timer()

    # Find extreme points (start of convex hull)
    sort_i = np.lexsort((points[:, 1], points[:, 0]))
    e1, e2 = points[sort_i[[0, -1]]]

    end_extreme = timer()

    # if main is not None:
    #     main.plot_point(e1, text="E1", color="blue")  # Debug
    #     main.plot_point(e2, text="E2", color="blue")  # Debug
    #     main.plot_connection(e1, e2, color="blue", temp=True)  # Debug

    ch_points = np.vstack((e1, e2))

    start_first = timer()

    # Split into 2 areas (start of recursion)
    s1 = []
    s2 = []
    for p in points:
        u = area_triangle(e1, p, e2)
        if u > 0:  # Left
            s1.append(p)
            # if main is not None:
            #     main.plot_point(p, text="1", color="blue")  # Debug
        elif u < 0:  # Right
            s2.append(p)
            # if main is not None:
            #     main.plot_point(p, text="2", color="blue")  # Debug

    end_first = timer()

    start_other = timer()

    # Find all other points
    if s1:
        sub_ch_points1 = quickhull_sub(s1, e1, e2, main=main)
        if sub_ch_points1.any():
            ch_points = np.vstack((ch_points, sub_ch_points1))
    if s2:
        sub_ch_points2 = quickhull_sub(s2, e2, e1, main=main)
        if sub_ch_points2.any():
            ch_points = np.vstack((ch_points, sub_ch_points2))

    end_other = timer()

    # Sort convex hull points based on angle from approximate center (for visualization)
    rands = np.random.choice(ch_points.shape[0], 3, replace=False)
    o = np.mean([ch_points[rands[0]], ch_points[rands[1]], ch_points[rands[2]]], axis=0)

    angles = []
    for p in ch_points:
        angle = np.arctan2(p[1] - o[1], p[0] - o[0])
        if angle < 0:
            angle += 2 * np.pi
        angles.append(angle)

    angles = np.array(angles)
    ch_points = ch_points[angles.argsort()]
    ch_points = np.vstack((ch_points, ch_points[0]))  # Connect first and last

    if main is not None:
        time_extreme = (end_extreme - start_extreme) * 1000
        time_first = (end_first - start_first) * 1000
        time_other = (end_other - start_other) * 1000
        main.log("Calculated convex hull on {} points using Quickhull algorithm in {} ms:"
                 .format(amount, int(time_extreme + time_first + time_other)))
        main.log("- Found first extreme points in {} ms".format(int(time_extreme)))
        main.log("- Split first areas in {} ms".format(int(time_first)))
        main.log("- Found all remaining points in {} ms".format(int(time_other)))

    return ch_points


def quickhull_sub(s, e1, e2, main=None):
    # Find biggest triangle area for s
    max_area, max_p, max_i = -np.inf, None, -1
    for i, p in enumerate(s):
        area = area_triangle(e1, p, e2)
        if almost_equal(area, max_area):
            # Take biggest angle if same area
            a = p - e1  # Vector from e1 to point
            b = e2 - p  # Vector from e2 to point
            angle1 = np.arctan2(b[1], b[0]) - np.arctan2(a[1], a[0])

            a = max_p - e1  # Vector from e1 to point
            b = e2 - max_p  # Vector from e2 to point
            angle2 = np.arctan2(b[1], b[0]) - np.arctan2(a[1], a[0])

            if angle1 > angle2:
                max_area, max_p, max_i = area, p, i

        elif area > max_area:
            max_area, max_p, max_i = area, p, i

    # if main is not None:
    #     main.plot_point(max_p, text="M", color="blue")  # Debug
    #     main.plot_connection(e1, max_p, color="blue", temp=True)  # Debug
    #     main.plot_connection(e2, max_p, color="blue", temp=True)  # Debug

    ch_points = np.array([max_p])

    # Split into 2 areas outside of triangle (ignoring points inside triangle)
    s1 = []
    s2 = []
    for p in s[:max_i] + s[(max_i + 1):]:
        u1 = area_triangle(e1, p, max_p)
        u2 = area_triangle(max_p, p, e2)
        if u1 > 0 and u2 < 0:  # Right of one line
            s1.append(p)
            # if main is not None:
            #     main.plot_point(p, text="1", color="blue")  # Debug
        elif u2 > 0 and u1 < 0:  # Right of the other line
            s2.append(p)
            # if main is not None:
            #     main.plot_point(p, text="2", color="blue")  # Debug

    if s1:
        sub_ch_points1 = quickhull_sub(s1, e1, max_p)
        if sub_ch_points1.any():
            ch_points = np.vstack((ch_points, sub_ch_points1))
    if s2:
        sub_ch_points2 = quickhull_sub(s2, max_p, e2)
        if sub_ch_points2.any():
            ch_points = np.vstack((ch_points, sub_ch_points2))

    return ch_points
