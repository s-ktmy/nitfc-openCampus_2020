from PyQt5 import QtCore, QtWidgets, QtGui


class logViewerWidget:

    def __init__(self, parent: QtWidgets.QWidget, name: str, pos: QtCore.QRect):
        self.widget = QtWidgets.QTextBrowser(parent)
        self.widget.setGeometry(pos)
        self.widget.setObjectName(name)

