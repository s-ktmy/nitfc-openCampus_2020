from PyQt5 import QtWidgets, QtCore, QtGui
from ..const import *
from ..Widget import logViewerWidget
from ..RNN.generateRNN import generateRNN
from pathlib import Path


class pianoRollWidget:

    def __init__(self, parent: QtWidgets.QWidget, name: str, pos: QtCore.QRect, logger: logViewerWidget):
        self.widget = pianoRollDrawer(parent, logger)
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

        self.logger = logger

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

    def stop(self):
        self.widget.stop()


class pianoRollDrawer(QtWidgets.QWidget):

    def __init__(self, parent=None, logger=None):
        super(pianoRollDrawer, self).__init__(parent)
        self.pianoRollImage = QtGui.QImage(r"assets\img\pianoroll.png")

        self.beat = 0
        self.logger = logger

        self.pianoRollObj = PianoRollObj(logger)

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
        self.clear()
        self.beat = 0

    def stop(self):
        self.measureTimer.stop()
        self.noteEvTimer.stop()

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
                if self.pianoRollObj.list[p][tick] == NOTELIST_START:
                    t = tick
                if self.pianoRollObj.list[p][tick] == NOTELIST_PAUSE:
                    if t != -1:
                        self.drawMidiBar(painter, p, t, tick - t)
                        t = -1
            if t != -1:
                self.drawMidiBar(painter, p, t, PIANOROLL_RESOLUTION - t)

        # ガイドラインを表示
        painter.setPen(QtCore.Qt.red)
        p = 1 - self.measureTimer.remainingTime() / self.measureMilliSec if self.measureTimer.isActive() else 0

        painter.drawLine(
            int(PIANOROLL_X_LENGTH / 4 * p + PIANOROLL_BASE_POS[0]),
            0,
            int(PIANOROLL_X_LENGTH / 4 * p + PIANOROLL_BASE_POS[0]),
            self.width()
        )

    def noteOn(self, pitch: int):
        self.pianoRollObj.noteOn(pitch)

    def noteOff(self, pitch: int):
        self.pianoRollObj.noteOff(pitch)

    def clear(self):
        if self.pianoRollObj.isInputted:
            inputData = self.pianoRollObj.getVector()
            self.logger.setText(inputData)
            self.pianoRollObj.guess(inputData)

        self.pianoRollObj.clear()

    def noteUpdate(self):
        self.beat += 1
        self.beat %= PIANOROLL_RESOLUTION

        self.pianoRollObj.noteUpdate(self.beat)


class PianoRollObj:
    def __init__(self, logger: logViewerWidget):
        self.list = [[
            0 for _ in range(PIANOROLL_RESOLUTION)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]

        self.isGuessed = False
        self.isInputted = False

        self.isPressedNotes = [False for _ in range(PIANOROLL_PITCH_NUMBER)]

        self.logger = logger

        self.model = generateRNN(
            modelPath=Path(r"assets/model/ckpt"),
            invDictPath=Path(r"assets/model/dict_inv.json")
        )

    def noteOn(self, pitch: int):
        assert pitch - PIANOROLL_LOWEST_NOTE < PIANOROLL_PITCH_NUMBER, "無効なMidi番号が指定されました"
        self.isPressedNotes[pitch - PIANOROLL_LOWEST_NOTE] = True

    def noteOff(self, pitch: int):
        assert pitch - PIANOROLL_LOWEST_NOTE < PIANOROLL_PITCH_NUMBER, "無効なMidi番号が指定されました"
        self.isPressedNotes[pitch - PIANOROLL_LOWEST_NOTE] = False

    def clear(self):
        self.list = [[
            0 for _ in range(PIANOROLL_RESOLUTION)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]
        self.isInputted = False

    def noteUpdate(self, beat):
        for p in range(PIANOROLL_PITCH_NUMBER):
            if self.isPressedNotes[p]:
                if beat == 0 or self.list[p][beat - 1] == 0:
                    self.list[p][beat] = NOTELIST_START
                    self.isInputted = True
                else:
                    self.list[p][beat] = NOTELIST_TIE

    def getVector(self):
        vector = []
        # 単音化リスト
        phoneList = [[
            0 for _ in range(PIANOROLL_RESOLUTION)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]

        for tick in range(PIANOROLL_RESOLUTION):
            flag = False
            for p in reversed(range(PIANOROLL_PITCH_NUMBER)):
                if (self.list[p][tick] != NOTELIST_PAUSE) and not flag:
                    phoneList[p][tick] = self.list[p][tick]
                    f = True

        t_ptr = 0
        p = 0
        while t_ptr < PIANOROLL_RESOLUTION:
            p_ptr = 0
            f = False
            for p in range(PIANOROLL_PITCH_NUMBER):
                if phoneList[p][t_ptr] == NOTELIST_START:
                    p_ptr = p
                    f = True
                    break
            if f:
                t = t_ptr
                while phoneList[p_ptr][t_ptr] != NOTELIST_PAUSE:
                    t_ptr += 1
                    if t_ptr == PIANOROLL_RESOLUTION:
                        break
                vector.append([p_ptr, (t_ptr - t) * 2])
            else:
                if len(vector) == 0:
                    vector.append([PIANOROLL_PAUSE_NOTEID, 2])
                else:
                    if vector[-1][0] != PIANOROLL_PAUSE_NOTEID:
                        vector.append([PIANOROLL_PAUSE_NOTEID, 2])
                    else:
                        vector[-1][1] += 2
                t_ptr += 1

        return vector

    def guess(self, seed_list: list):
        # モデルを利用した推測をここに書く
        self.isGuessed = True
        seed = []
        for pr in seed_list:
            seed.append((min(pr[0] + PIANOROLL_LOWEST_NOTE, PIANOROLL_PAUSE_NOTEID), pr[1]))
        geneData = self.model.generate(seed)
        self.logger.setText(geneData)
