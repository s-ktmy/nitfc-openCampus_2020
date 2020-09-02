from PyQt5 import QtCore, QtWidgets, QtGui


class configWidget:

    def __init__(self, parent: QtWidgets.QWidget, name: str, title: str, pos: QtCore.QRect):
        self.widget = QtWidgets.QGroupBox(parent)
        self.widget.setGeometry(pos)
        self.widget.setObjectName(name)

        self.widget.setTitle(title)

