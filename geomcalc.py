#!/usr/bin/env python3

import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modes import points_lines as pl


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        tabs = QTabWidget()
        tabs.setFixedHeight(100)

        # Points and lines
        self.pl = pl.PointsLines()

        tab_pl = QWidget()
        tabs.addTab(tab_pl, "Points & Lines")

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
            txt_px.textChanged.connect(lambda: self.pl_update_ui(self.pl, self.txt_points))
            txt_py = QLineEdit()
            txt_py.setText("0")
            txt_py.setMaximumWidth(50)
            txt_py.textChanged.connect(lambda: self.pl_update_ui(self.pl, self.txt_points))

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

        # Convex Hulls
        tab_ch = QWidget()
        tabs.addTab(tab_ch, "Convex Hulls")

        # Graph space
        self.figure = Figure()
        FigureCanvas(self.figure)
        self.figure.canvas.mpl_connect("button_press_event", self.on_plot_click)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
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
            print("TODO plot points: {}, {}".format(event.xdata, event.ydata))

    def pl_update_ui(self, pl, txt_points):
        if pl.mode == 0:
            [[p.setDisabled(True) for p in points] for points in txt_points[2:]]
        elif pl.mode == 1:
            [[p.setDisabled(True) for p in points] for points in txt_points[3:]]
            [p.setDisabled(False) for p in txt_points[2]]
        elif pl.mode == 2:
            [[p.setDisabled(False) for p in points] for points in txt_points[2:]]

        try:
            points = [(float(txt_point[0].text()), float(txt_point[1].text())) for txt_point in txt_points]
        except ValueError:
            print("Error! Invalid points data!")
            return
        else:
            self.pl.set_points(points)

    def pl_calculate(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Points & Lines Result")

        result, text, p5, closest = self.pl.calculate()

        if p5 is not None:
            print("TODO plot p5")
        if closest is not None:
            print("TODO plot line from p5 to closest")

        msg.setText(text)
        msg.exec()


if __name__ == "__main__":
    # Create Qt application with window
    app = QApplication(sys.argv)
    main_win = MainWindow()

    # Execute application (blocking)
    app.exec_()

    sys.exit(0)
