from PyQt5 import QtCore, QtWidgets, QtGui
from collections import deque
from ..const import *


class logViewerWidget:

    def __init__(self, parent: QtWidgets.QWidget, name: str, pos: QtCore.QRect):
        self.widget = QtWidgets.QTextBrowser(parent)
        self.widget.setGeometry(pos)
        self.widget.setObjectName(name)
        self.log = deque()
        self.scrollBar = self.widget.verticalScrollBar()

    def setText(self, text: any):
        if type(text) is not str:
            text = str(text)
        self.log.append(text)
        if len(self.log) > LOG_ROW_NUMBER:
            self.log.popleft()
        self.widget.setText("\n".join(self.log))
        self.scrollBar.setValue(self.scrollBar.maximum())
