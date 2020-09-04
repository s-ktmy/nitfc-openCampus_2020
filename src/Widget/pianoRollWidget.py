from PyQt5 import QtWidgets, QtCore, QtGui
from ..const import *


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

        self.frameTimer = QtCore.QTimer(parent)
        self.frameTimer.setInterval(PIANOROLL_UPDATE_TIME)
        self.frameTimer.setSingleShot(False)
        self.frameTimer.timeout.connect(self.update)
        self.frameTimer.start()

    def noteOn(self, pitch):
        self.widget.noteOn(pitch)

    def noteOff(self, pitch):
        self.widget.noteOff(pitch)

    def noteClear(self):
        self.widget.clear()

    def update(self):
        self.widget.update()

    def play(self):
        #self.frameTimer.start()
        self.widget.play()


class pianoRollDrawer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(pianoRollDrawer, self).__init__(parent)
        self.pianoRollImage = QtGui.QImage(r"assets\img\pianoroll.png")
        self.noteList = [[
            0 for _ in range(PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]
        self.beat = 0

        self.isPressedNotes = [False for _ in range(PIANOROLL_PITCH_NUMBER)]

        self.measureMilliSec = int(1000 * 240 / PIANOROLL_BPM)

        self.noteEvTimer = QtCore.QTimer(parent)
        self.noteEvTimer.setInterval(int(self.measureMilliSec) / PIANOROLL_RESOLUTION)
        self.noteEvTimer.setSingleShot(False)
        self.noteEvTimer.timeout.connect(self.noteUpdate)

        self.measureTimer = QtCore.QTimer(parent)
        self.measureTimer.setInterval(self.measureMilliSec)
        self.measureTimer.setSingleShot(False)
        self.measureTimer.timeout.connect(self.clear)

    def play(self):
        self.measureTimer.start()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.pianoRollImage)
        painter.setPen(QtCore.Qt.red)
        painter.setBrush(QtCore.Qt.yellow)
        p = 1 - self.measureTimer.remainingTime() / self.measureMilliSec
        painter.drawLine(int(320 * p + 61), 0, int(320 * p + 61), self.width())

    def noteOn(self, pitch: int):
        assert pitch - PIANOROLL_LOWEST_NOTE > PIANOROLL_PITCH_NUMBER, "無効なMidi番号が指定されました"
        self.isPressedNotes[pitch - PIANOROLL_LOWEST_NOTE] = True

    def noteOff(self, pitch: int):
        assert pitch - PIANOROLL_LOWEST_NOTE > PIANOROLL_PITCH_NUMBER, "無効なMidi番号が指定されました"
        self.isPressedNotes[pitch - PIANOROLL_LOWEST_NOTE] = False

    def clear(self):
        self.noteList = [[
            0 for _ in range(PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]

    def noteUpdate(self):
        for p in PIANOROLL_PITCH_NUMBER:
            if self.isPressedNotes[p]:
                if self.beat == 0 or self.noteList[self.beat - 1] == 0:
                    self.noteList[0][p][self.beat] = 1
                else:
                    self.noteList[0][p][self.beat] = 2

        self.beat += 1
        self.beat %= PIANOROLL_RESOLUTION
