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
        # self.frameTimer.start()
        self.widget.play()


class pianoRollDrawer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(pianoRollDrawer, self).__init__(parent)
        self.pianoRollImage = QtGui.QImage(r"assets\img\pianoroll.png")
        self.noteList = [[
            0 for _ in range(PIANOROLL_RESOLUTION)
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
        self.noteEvTimer.start()

    @staticmethod
    def drawMidiBar(painter: QtGui.QPainter, pitch: int, start: int, length: int):
        painter.drawRect(
            PIANOROLL_BASE_POS[0] + start * PIANOROLL_OBJ_SIZE[0],
            PIANOROLL_BASE_POS[1] - pitch * PIANOROLL_OBJ_SIZE[1],
            PIANOROLL_OBJ_SIZE[0] * length,
            PIANOROLL_OBJ_SIZE[1]
        )

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        # 背景画像描画
        painter.drawImage(0, 0, self.pianoRollImage)

        # 入力されたノートを表示
        painter.setPen(QtCore.Qt.blue)
        painter.setBrush(QtCore.Qt.cyan)

        for p in range(PIANOROLL_PITCH_NUMBER):
            t = -1
            for tick in range(PIANOROLL_RESOLUTION):
                if self.noteList[p][tick] == NOTELIST_START:
                    t = tick
                if self.noteList[p][tick] == NOTELIST_PAUSE:
                    if t != -1:
                        self.drawMidiBar(painter, p, t, tick - t)
                        t = -1
            if t != -1:
                self.drawMidiBar(painter, p, t, PIANOROLL_RESOLUTION - t)

        # ガイドラインを表示
        painter.setPen(QtCore.Qt.red)
        p = 1 - self.measureTimer.remainingTime() / self.measureMilliSec

        painter.drawLine(
            int(PIANOROLL_X_LENGTH / 2 * p + PIANOROLL_BASE_POS[0]),
            0,
            int(PIANOROLL_X_LENGTH / 2 * p + PIANOROLL_BASE_POS[0]),
            self.width()
        )

    def noteOn(self, pitch: int):
        assert pitch - PIANOROLL_LOWEST_NOTE < PIANOROLL_PITCH_NUMBER, "無効なMidi番号が指定されました"
        self.isPressedNotes[pitch - PIANOROLL_LOWEST_NOTE] = True

    def noteOff(self, pitch: int):
        assert pitch - PIANOROLL_LOWEST_NOTE < PIANOROLL_PITCH_NUMBER, "無効なMidi番号が指定されました"
        self.isPressedNotes[pitch - PIANOROLL_LOWEST_NOTE] = False

    def clear(self):
        self.noteList = [[
            0 for _ in range(PIANOROLL_RESOLUTION)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]

    def noteUpdate(self):
        self.beat += 1
        self.beat %= PIANOROLL_RESOLUTION

        for p in range(PIANOROLL_PITCH_NUMBER):
            if self.isPressedNotes[p]:
                if self.beat == 0 or self.noteList[p][self.beat - 1] == 0:
                    self.noteList[p][self.beat] = NOTELIST_START
                else:
                    self.noteList[p][self.beat] = NOTELIST_TIE
