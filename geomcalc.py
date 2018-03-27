#!/usr/bin/env python3

import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modes import points_lines as pl


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
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
        self.tabs.addTab(tab_pl, "Points & Lines")

        self.cb_type = QComboBox()
        self.cb_type.setToolTip("Input type")
        self.cb_type.addItems(["1 point", "1 point, 1 line", "2 lines"])
        self.cb_type.currentIndexChanged.connect(lambda: self.pl.set_mode(self.cb_type.currentIndex()))
        self.cb_type.currentIndexChanged.connect(lambda: self.pl_update_ui(self.pl, self.txt_points))

        tab_pl.layout = QHBoxLayout()
        tab_pl.layout.addWidget(self.cb_type)
        tab_pl.layout.addStretch()

        self.txt_points = []  # List of tuples (elements)
        for i in range(1, 5):
            lbl_p = QLabel("P{}:".format(i))
            txt_px = QLineEdit()
            txt_px.setText("0")
            txt_px.setMaximumWidth(50)
            txt_px.editingFinished.connect(lambda: self.pl_update_ui(self.pl, self.txt_points, replot=True))
            txt_py = QLineEdit()
            txt_py.setText("0")
            txt_py.setMaximumWidth(50)
            txt_py.editingFinished.connect(lambda: self.pl_update_ui(self.pl, self.txt_points, replot=True))

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
        tab_ch = QWidget()
        self.tabs.addTab(tab_ch, "Convex Hulls")

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        vbox.addWidget(self.figure.canvas)

        # Window
        self.setLayout(vbox)
        self.setGeometry(300, 300, 1000, 600)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowTitle("Geometry Calculator")
        self.show()

    def on_plot_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            if self.tabs.currentIndex() == 0:
                if len(self.plot.patches) > self.pl.mode + 1:
                    self.plot_clear()
                self.plot_point(event.xdata, event.ydata)
                self.pl_update_ui(self.pl, self.txt_points, replot=False)

    def on_plot_resize(self, event):
        self.plot.set_xlim((0, event.width))
        self.plot.set_ylim((0, event.height))

    def plot_clear(self):
        [patch.remove() for patch in self.plot.patches[::-1]]
        [text.remove() for text in self.plot.texts[::-1]]

    def plot_point(self, x, y, text="", color="black"):
        rect = Rectangle((x, y), 5, 5, color=color)
        self.plot.add_patch(rect)

        npatches = len(self.plot.patches)
        text = "P{}".format(npatches) if not text else text
        self.plot.text(x + 7, y - 5, text, fontsize=9, color=color)
        self.figure.canvas.draw()

        self.txt_points[npatches - 1][0].setText(str(int(x)))
        self.txt_points[npatches - 1][1].setText(str(int(y)))

    def pl_update_ui(self, pl, txt_points, replot=False):
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
            self.plot_clear()
            for point in points[:self.pl.mode + 2]:
                self.plot_point(point[0], point[1])

    def pl_calculate(self):
        self.pl_update_ui(self.pl, self.txt_points, replot=True)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Points & Lines Result")

        result, text, pp, closest = self.pl.calculate()

        if pp is not None:
            self.plot_point(pp[0], pp[1], text="PP", color="red")
        if np.array_equal(closest, pp):
            print("TODO plot line from p1 to pp")
        else:
            print("TODO plot line from p1 to closest")

        msg.setText(text)
        msg.exec()

        self.pl_update_ui(self.pl, self.txt_points, replot=True)


if __name__ == "__main__":
    # Create Qt application with window
    app = QApplication(sys.argv)
    main_win = MainWindow()

    # Execute application (blocking)
    app.exec_()

    sys.exit(0)
