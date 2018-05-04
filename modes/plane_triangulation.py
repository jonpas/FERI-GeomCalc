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
            return mwt(self.points), (np.array([]), np.array([]))
        elif self.algorithm == 1:
            return np.array([]), hamiltonian_path(self.points, main=self.parent)


def mwt(points):
    if len(points) < 2:
        return np.array([])

    # Generate convex hull (for algorithm end check)
    ch_points = len(ch.quickhull(points)) - 1  # -1 from final connection

    # Generate all possible lines
    lines = []
    distances = []
    for i, p1 in enumerate(points):
        for p2 in points[i + 1:]:
            lines.append([p1, p2])
            distances.append(pl.euclidean_dist(p1, p2))

    # Sort lines by distance (shortest to longest)
    lines = np.array(lines)
    distances = np.array(distances)
    lines = lines[distances.argsort()]

    # Shortest line is definitely part of triangulation
    pt_lines = [lines[0]]
    lines = lines[1:]

    # Accept lines that don't intersect already accepted lines, reject others
    # Repeat until enough lines are accepted (3 * points - 3 - convex hull points)
    while len(pt_lines) < 3 * len(points) - 3 - ch_points:
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


def hamiltonian_path(points, main=None):
    # Generate convex hulls and spiral list
    ch_points = []
    s_points = []
    while len(points) > 0:
        # Generate convex hull (without last connecting point)
        ch_p = ch.quickhull(points)[:-1]

        # Find max Y and roll hull around to have max Y as first element
        ch_max_i = np.lexsort((ch_p[:, 0], ch_p[:, 1]))[-1]  # Max Y point's index
        ch_p = np.roll(ch_p, -ch_max_i, axis=0)

        # Assure first point in inner hull forms convex angle
        if len(s_points) > 0 and len(ch_p) > 1:
            # Roll until convex angle (one roll might not be enough)
            angle = -1
            while angle < 0:
                a = s_points[-1] - ch_p[0]  # Vector from last point of outer hull to first point in inner hull
                b = ch_p[0] - ch_p[1]  # Vector from first point to second point in inner hull
                angle = np.arctan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1])  # Angle between above vectors

                # Roll by one so wanted point becomes first
                if angle < 0:
                    ch_p = np.roll(ch_p, -1, axis=0)

                    # if main is not None:
                    #     main.plot_point(ch_p[-1], text="O")  # Debug
                    #     main.plot_point(ch_p[0], text="R")  # Debug

        # Assure spiral doesn't intersect itself
        if len(ch_points) > 0:
            ch_last = ch_points[-1]
            first, last, inner = ch_last[0], ch_last[-1], ch_p[0]

            for i, p in enumerate(ch_p[:-1]):
                pi, itype = pl.intersection(last, inner, p, ch_p[i + 1])
                if itype == "intersection":
                    # Insert point high enough between first and last point of outer hull
                    offset_factor = (inner[1] - last[1]) / (first[1] - last[1])
                    x_offset = (last[0] - first[0]) * offset_factor
                    new_p = [last[0] - x_offset, inner[1]]

                    # Insert to outer hull (not part of inner hull!) and spiral
                    ch_points[-1] = np.vstack((ch_last, [new_p]))
                    s_points.append(np.array(new_p))

                    # if main is not None:
                    #     main.plot_connection(first, last, color="blue")  # Debug
                    #     main.plot_point(last, color="red", text="I")  # Debug
                    #     main.plot_point(new_p, color="red", text="O")  # Debug

                    break

        # Add to forming spiral and hulls list
        s_points.extend(ch_p)
        ch_points.append(ch_p)

        # Remove convex hull points from left-over points
        points = np.array([p for p in points if p not in ch_p])

    # Generate generalized triangle strip
    # Indexes of last point in first hull, first points in second and first hulls
    a, b, c = len(ch_points[0]) - 1, len(ch_points[0]), 0
    pt_points = [s_points[a], s_points[b], s_points[c]]

    while a != b:
        # Check if new line intersects spiral list or already created lines
        line = [pt_points[-1], s_points[c]]
        intersection = False
        for i, p in enumerate(s_points[:-1]):
            pi, itype = pl.intersection(line[0], line[1], p, s_points[i + 1])
            if itype == "intersection":
                intersection = True
                break
        if not intersection:
            for i, p in enumerate(pt_points[:-1]):
                pi, itype = pl.intersection(line[0], line[1], p, pt_points[i + 1])
                if itype == "intersection":
                    intersection = True
                    break

        # Degenerate
        if intersection:
            c = a

        pt_points.append(s_points[c])

        # Move to next triangle
        a, b = b, c
        c = a + 1

        # Degenerate on final point
        if c >= len(s_points):
            c = a
            pt_points.append(s_points[c])

    return np.array(s_points), np.array(pt_points)
