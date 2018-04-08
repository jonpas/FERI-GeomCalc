#!/usr/bin/env python3

import sys
import numpy as np
from timeit import default_timer as timer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, ConnectionPatch
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modes import points_lines as pl
from modes import convex_hulls as ch


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.txt_points = []  # List of tuples (elements)
        self.lines = []  # List of tuples (points)

        self.initUI()

    def initUI(self):
        # Log
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)

        # Graph space
        self.figure = Figure()
        FigureCanvas(self.figure)
        self.figure.canvas.mpl_connect("button_press_event", self.on_plot_click)
        self.figure.canvas.mpl_connect("resize_event", self.on_plot_resize)

        self.plot = self.figure.add_subplot(111)
        self.plot.tick_params(axis="both", which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
        self.figure.tight_layout()

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFixedHeight(100)

        # Tab - Points and lines
        self.pl = pl.PointsLines()

        tab_pl = QWidget()
        self.tabs.addTab(tab_pl, "Points && Lines")

        self.cb_type = QComboBox()
        self.cb_type.setToolTip("Input type")
        self.cb_type.addItems(["1 point", "1 point, 1 line", "2 lines"])
        self.cb_type.currentIndexChanged.connect(self.pl_set_mode)

        tab_pl.layout = QHBoxLayout()
        tab_pl.layout.addWidget(self.cb_type)
        tab_pl.layout.addStretch()

        for i in range(1, 5):
            lbl_p = QLabel("P{}:".format(i))
            txt_px = QLineEdit()
            txt_px.setText("0")
            txt_px.setMaximumWidth(50)
            txt_px.setValidator(QIntValidator(0, 2147483647))
            txt_px.editingFinished.connect(lambda: self.pl_update_ui(self.pl, self.txt_points, replot=True, reset=True))
            txt_py = QLineEdit()
            txt_py.setText("0")
            txt_py.setMaximumWidth(50)
            txt_py.setValidator(QIntValidator(0, 2147483647))
            txt_py.editingFinished.connect(lambda: self.pl_update_ui(self.pl, self.txt_points, replot=True, reset=True))

            self.txt_points.append((txt_px, txt_py))

            tab_pl.layout.addWidget(lbl_p)
            tab_pl.layout.addWidget(txt_px)
            tab_pl.layout.addWidget(txt_py)
            tab_pl.layout.addSpacing(10)

        tab_pl.layout.addStretch()

        btn_calc = QPushButton("Calculate")
        btn_calc.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        btn_calc.clicked.connect(self.pl_calculate)

        tab_pl.layout.addWidget(btn_calc)
        tab_pl.setLayout(tab_pl.layout)

        self.pl_update_ui(self.pl, self.txt_points)

        # Tab - Convex Hulls
        self.ch = ch.ConvexHulls()

        tab_ch = QWidget()
        self.tabs.addTab(tab_ch, "Convex Hulls")

        self.cb_distribution = QComboBox()
        self.cb_distribution.setToolTip("Point distribution")
        self.cb_distribution.addItems(["Uniform", "Normal (Gaussian)"])
        self.cb_distribution.setMaximumWidth(100)

        lbl_pamount = QLabel("Amount:")
        self.txt_pamount = QLineEdit()
        self.txt_pamount.setText("100")
        self.txt_pamount.setToolTip("Amount of points")
        self.txt_pamount.setMaximumWidth(50)
        self.txt_pamount.setValidator(QIntValidator(0, 2147483647))

        btn_pgenerate = QPushButton("Generate Points")
        btn_pgenerate.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        btn_pgenerate.clicked.connect(self.generate_points)

        self.cb_convexalg = QComboBox()
        self.cb_convexalg.setToolTip("Algorithm")
        self.cb_convexalg.addItems(["Jarvis March", "Graham Scan", "Quickhull"])
        self.cb_convexalg.setMaximumWidth(100)
        self.cb_convexalg.currentIndexChanged.connect(self.ch_set_algorithm)

        btn_convexcalc = QPushButton("Calculate")
        btn_convexcalc.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        btn_convexcalc.clicked.connect(self.ch_calculate)

        tab_ch.layout = QHBoxLayout()
        tab_ch.layout.addWidget(self.cb_distribution)
        tab_ch.layout.addWidget(lbl_pamount)
        tab_ch.layout.addWidget(self.txt_pamount)
        tab_ch.layout.addWidget(btn_pgenerate)
        tab_ch.layout.addStretch()
        tab_ch.layout.addWidget(self.cb_convexalg)
        tab_ch.layout.addWidget(btn_convexcalc)
        tab_ch.setLayout(tab_ch.layout)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        vbox.addWidget(self.figure.canvas)
        vbox.addWidget(self.txt_log)

        # Window
        self.setLayout(vbox)
        self.setGeometry(300, 300, 1000, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowTitle("Geometry Calculator")
        self.show()

    def log(self, text):
        self.txt_log.append(str(text))
        print("LOG: {}".format(text))

    def on_plot_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            if self.tabs.currentIndex() == 0:
                npatches = len(self.plot_get_points())
                if npatches > self.pl.mode + 1:
                    self.plot_clear()
                self.plot_point((event.xdata, event.ydata), text="P", num=True)
                if self.pl.mode == 1 and npatches == 2:
                    self.plot_line(self.pl.p2, (event.xdata, event.ydata))
                elif self.pl.mode == 2:
                    if npatches == 1:
                        self.plot_line(self.pl.p1, (event.xdata, event.ydata))
                    elif npatches == 3:
                        self.plot_line(self.pl.p3, (event.xdata, event.ydata))
                self.pl_update_ui(self.pl, self.txt_points, replot=False)

    def on_plot_resize(self, event):
        self.plot.set_xlim((0, event.width))
        self.plot.set_ylim((0, event.height))

    def plot_get_points(self):
        return [p for p in self.plot.patches if isinstance(p, Rectangle)]

    def plot_get_lines(self):
        return [p for p in self.plot.patches if isinstance(p, ConnectionPatch)]

    def plot_clear(self, force=False):
        [patch.remove() for patch in self.plot.patches[::-1]]
        [text.remove() for text in self.plot.texts[::-1]]
        self.lines = []

        if force:
            self.figure.canvas.draw()

    def plot_point(self, p, text="", num=False, color="black"):
        x, y = p
        rect = Rectangle((int(x) - 2, int(y) - 2), 4, 4, color=color)
        self.plot.add_patch(rect)

        npatches = len(self.plot_get_points())
        text = "{}{}".format(text, npatches if num else "")
        self.plot.text(int(x) + 7, int(y) - 5, text, fontsize=9, color=color)
        self.figure.canvas.draw()

        if self.tabs.currentIndex() == 0 and npatches <= len(self.txt_points):
            self.txt_points[npatches - 1][0].setText(str(int(x)))
            self.txt_points[npatches - 1][1].setText(str(int(y)))

    def plot_line(self, p1, p2, color="black", temp=False):
        line = ConnectionPatch(p1, p2, coordsA="data", coordsB="data", color=color)
        self.plot.add_patch(line)
        self.figure.canvas.draw()

        if not temp:
            self.lines.append((p1, p2))

    def generate_points(self):
        self.plot_clear(force=True)

        if not self.txt_pamount.text():
            print("Invalid amount of points!")
            return

        amount = int(self.txt_pamount.text())
        distribution = self.cb_distribution.currentIndex()

        start = timer()
        if distribution == 0:
            # Uniform
            points = []
        else:
            # Normal (Gaussian)
            points = []
        end = timer()

        self.ch.set_points(points)
        [self.plot_point(p) for p in points]

        self.log("Generated {} points in {} ms".format(amount, int(end - start)))

    def pl_update_ui(self, pl, txt_points, replot=False, reset=False):
        # Toggle available points based on mode
        if pl.mode == 0:
            [[p.setDisabled(True) for p in points] for points in txt_points[2:]]
        elif pl.mode == 1:
            [[p.setDisabled(True) for p in points] for points in txt_points[3:]]
            [p.setDisabled(False) for p in txt_points[2]]
        elif pl.mode == 2:
            [[p.setDisabled(False) for p in points] for points in txt_points[2:]]

        # Get point coordinates
        try:
            points = [(float(txt_point[0].text()), float(txt_point[1].text())) for txt_point in txt_points]
        except ValueError:
            print("Error! Invalid points data!")
            return
        else:
            self.pl.set_points(points)

        if replot:
            # (Re)plot all points
            lines = self.lines
            self.plot_clear()
            [self.plot_point(point, text="P", num=True) for point in points[:self.pl.mode + 2]]

            if reset:
                # Replot missing lines in case of reset
                npatches = len(self.plot_get_points())
                if self.pl.mode > 0:
                    if npatches > 1:
                        if self.pl.mode == 1:
                            self.plot_line(self.pl.p2, self.pl.p3)
                        else:
                            self.plot_line(self.pl.p1, self.pl.p2)
                    if npatches > 3:
                        self.plot_line(self.pl.p3, self.pl.p4)
            else:
                [self.plot_line(line[0], line[1]) for line in lines]

    def pl_calculate(self):
        self.pl_update_ui(self.pl, self.txt_points, replot=True)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Points & Lines Result")

        result, text, p1, p2, point_txt = self.pl.calculate()

        if p1 is not None:
            if point_txt == "line":
                self.plot_line(p1, p2, color="red")
            else:
                self.plot_point(p1, text=point_txt, color="red")
                if np.array_equal(p2, p1):
                    self.plot_line(self.pl.p1, p1, temp=True)
                elif p2 is not None:
                    self.plot_line(self.pl.p1, p2, temp=True)

        msg.setText(text)
        msg.exec()

        self.pl_update_ui(self.pl, self.txt_points, replot=True)

    def pl_set_mode(self):
        self.plot_clear(force=True)
        self.pl.set_mode(self.cb_type.currentIndex())
        self.pl_update_ui(self.pl, self.txt_points)

    def ch_calculate(self):
        self.ch.calculate()

    def ch_set_algorithm(self):
        self.plot_clear(force=True)
        self.ch.set_algorithm(self.cb_convexalg.currentIndex())


if __name__ == "__main__":
    # Create Qt application with window
    app = QApplication(sys.argv)
    main_win = MainWindow()

    # Execute application (blocking)
    app.exec_()

    sys.exit(0)
