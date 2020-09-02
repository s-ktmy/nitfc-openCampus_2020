from PyQt5 import QtWidgets, QtCore, QtGui


class pianoRollWidget:

    def __init__(self, parent: QtWidgets.QWidget, name: str, pos: QtCore.QRect):
        self.widget = pianoRollDrawer(parent)
        self.widget.setGeometry(pos)

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)

        self.widget.setPalette(palette)
        self.widget.setAutoFillBackground(True)
        self.widget.setObjectName(name)

        self.widget.raise_()

        self.timer = QtCore.QTimer(parent)
        self.timer.setInterval(20)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.update)

        self.timer.start()

    def update(self):
        self.widget.update()


class pianoRollDrawer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(pianoRollDrawer, self).__init__(parent)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.red)
        painter.setBrush(QtCore.Qt.yellow)
        painter.drawRect(10, 10, 100, 100)
