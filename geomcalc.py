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
