#!/usr/bin/env python3

import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        tabs = QTabWidget()
        tabs.setMinimumHeight(100)
        tab_int = QWidget()
        tab_hull = QWidget()
        tabs.addTab(tab_int, "Intersections")
        tabs.addTab(tab_hull, "Convex Hulls")

        # Intersections
        cb_type = QComboBox()
        cb_type.setToolTip("Mode")
        cb_type.addItems(["1 point", "1 point, 1 line", "2 lines"])

        lbl_p1x = QLabel("P1 (x):")
        txt_p1x = QLineEdit()
        txt_p1x.setMaximumWidth(50)
        lbl_p1y = QLabel("P1 (y):")
        txt_p1y = QLineEdit()
        txt_p1y.setMaximumWidth(50)

        tab_int.layout = QHBoxLayout()
        tab_int.layout.addWidget(cb_type)
        tab_int.layout.addStretch()
        tab_int.layout.addWidget(lbl_p1x)
        tab_int.layout.addWidget(txt_p1x)
        tab_int.layout.addWidget(lbl_p1y)
        tab_int.layout.addWidget(txt_p1y)
        tab_int.layout.addStretch()
        tab_int.setLayout(tab_int.layout)

        # Convex Hulls

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
