from PyQt5 import QtWidgets, QtCore
from .centralWidget import centralWidget


class mainWindow:

    def __init__(self):
        # Window
        self.window = QtWidgets.QMainWindow()
        self.window.setObjectName("MainWindow")
        self.window.resize(1000, 640)
        self.window.setMinimumSize(QtCore.QSize(1000, 640))
        self.window.setMaximumSize(QtCore.QSize(1000, 640))
        self.window.setBaseSize(QtCore.QSize(1024, 768))

        # centralWidget
        self.centralWidget = centralWidget(self.window, "centralWidget")

        self.window.setCentralWidget(self.centralWidget.widget)
        QtCore.QMetaObject.connectSlotsByName(self.window)

    def show(self):
        self.window.show()

    def draw(self):
        pass
