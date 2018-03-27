#!/usr/bin/env python3

import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *

from modes import points_lines as pl


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        tabs = QTabWidget()
        tabs.setMinimumHeight(100)

        # Points and lines
        tab_pl = QWidget()
        tabs.addTab(tab_pl, "Points & Lines")

        cb_type = QComboBox()
        cb_type.setToolTip("Input type")
        cb_type.addItems(["1 point", "1 point, 1 line", "2 lines"])

        tab_pl.layout = QHBoxLayout()
        tab_pl.layout.addWidget(cb_type)
        tab_pl.layout.addStretch()

        txt_points = []  # List of tuples
        for i in range(1,5):
            lbl_p = QLabel("P{}:".format(i))
            txt_px = QLineEdit()
            txt_px.setMaximumWidth(50)
            txt_py = QLineEdit()
            txt_py.setMaximumWidth(50)
            txt_points.append((txt_px, txt_py))

            tab_pl.layout.addWidget(lbl_p)
            tab_pl.layout.addWidget(txt_px)
            tab_pl.layout.addWidget(txt_py)
        tab_pl.layout.addStretch()

        self.pl = pl.PointsLines(txt_points)

        btn_calc = QPushButton("Calculate")
        btn_calc.clicked.connect(self.pl.calculate)

        tab_pl.layout.addWidget(btn_calc)
        tab_pl.setLayout(tab_pl.layout)

        # Convex Hulls
        tab_ch = QWidget()
        tabs.addTab(tab_ch, "Convex Hulls")

        # Graph space
        self.figure = Figure()
        FigureCanvas(self.figure)
        self.figure.canvas.setMinimumHeight(200)
        self.figure.canvas.setMinimumWidth(400)
        # self.figure.canvas.mpl_connect("button_press_event", self.on_plot_click)
        # self.figure.canvas.mpl_connect("motion_notify_event", self.on_plot_over)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
        vbox.addWidget(self.figure.canvas)

        # Window
        self.setLayout(vbox)
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("Geometry Calculator")
        self.show()


if __name__ == "__main__":
    # Create Qt application with window
    app = QApplication(sys.argv)
    main_win = MainWindow()

    # Execute application (blocking)
    app.exec_()

    sys.exit(0)
