from PyQt5 import QtWidgets, QtCore, QtGui
from ..const import *
from ..Widget import logViewerWidget
from ..RNN.generateRNN import generateRNN
from pathlib import Path


class pianoRollWidget:

    def __init__(self, parent: QtWidgets.QWidget, parentObj, name: str, pos: QtCore.QRect, logger: logViewerWidget):
        self.parentObj = parentObj

        self.widget = pianoRollDrawer(
            parent=parent,
            parentObj=self,
            logger=logger
        )
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

    def songPlay(self):
        self.widget.isPlaying = True
        self.widget.beatTimer.start()

    def setMidiPlayer(self, midiPlayer):
        self.widget.setMidiPlayer(midiPlayer)


class pianoRollDrawer(QtWidgets.QWidget):

    def __init__(self, parent=None, parentObj=None, logger=None):
        super(pianoRollDrawer, self).__init__(parent)
        self.pianoRollImage = QtGui.QImage(r"assets\img\pianoroll.png")

        self.parentObj = parentObj

        self.beat = 0
        self.logger = logger

        self.pianoRollObj = PianoRollObj(self, logger)

        self.measureMilliSec = int(1000 * 240 / PIANOROLL_BPM)

        self.isPlaying = False
        self.midiPlayer = None

        # Keyイベント用タイマー
        self.noteEvTimer = QtCore.QTimer(parent)
        self.noteEvTimer.setInterval(int(self.measureMilliSec) / PIANOROLL_RESOLUTION)
        self.noteEvTimer.setSingleShot(False)
        self.noteEvTimer.timeout.connect(self.noteUpdate)

        # 小節終了検知用タイマー
        self.measureTimer = QtCore.QTimer(parent)
        self.measureTimer.setInterval(self.measureMilliSec)
        self.measureTimer.setSingleShot(False)
        self.measureTimer.timeout.connect(self.clear)

        # 曲再生時拍子管理用タイマー
        self.beatTimer = QtCore.QTimer(parent)
        self.beatTimer.setInterval(int(self.measureMilliSec) / PIANOROLL_RESOLUTION)
        self.beatTimer.setSingleShot(False)
        self.beatTimer.timeout.connect(self.playSong)

    def play(self):
        self.measureTimer.start()
        self.noteEvTimer.start()
        self.pianoRollObj.isInputted = False
        self.pianoRollObj.isGuessed = False
        self.pianoRollObj.pressingReset()
        self.clear()
        self.beat = 0

    def stop(self):
        self.measureTimer.stop()
        self.noteEvTimer.stop()

    def setMidiPlayer(self, midiPlayer):
        self.midiPlayer = midiPlayer

    @staticmethod
    def drawMidiBar(painter: QtGui.QPainter, pitch: int, start: int, length: int):
        if start < PIANOROLL_RESOLUTION:
            painter.setPen(QtGui.QColor(0, 0, 255))
            painter.setBrush(QtGui.QColor(153, 170, 255))
        else:
            painter.setPen(QtGui.QColor(255, 0, 0))
            painter.setBrush(QtGui.QColor(255, 153, 204))
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
        for p in range(PIANOROLL_PITCH_NUMBER):
            t = -1
            for tick in range(PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER):
                if self.pianoRollObj.list[p][tick] == NOTELIST_START:
                    if t != -1:
                        self.drawMidiBar(painter, p, t, tick - t)
                    t = tick
                if self.pianoRollObj.list[p][tick] == NOTELIST_PAUSE:
                    if t != -1:
                        self.drawMidiBar(painter, p, t, tick - t)
                        t = -1
            if t != -1:
                self.drawMidiBar(painter, p, t, PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER - t)

        # ガイドラインを表示
        painter.setPen(QtCore.Qt.red)
        if not self.isPlaying:
            p = 1 - self.measureTimer.remainingTime() / self.measureMilliSec if self.measureTimer.isActive() else 0
        else:
            p = max(0, (1 - self.beatTimer.remainingTime() / (
                        int(self.measureMilliSec) / PIANOROLL_RESOLUTION) + self.beat - 1) / 16)

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
        self.beat = 0
        if self.pianoRollObj.isInputted:
            inputData = self.pianoRollObj.getVector()
            self.logger.setText(inputData)
            self.pianoRollObj.guess(inputData)
        else:
            self.pianoRollObj.clear()

    def noteUpdate(self):
        if self.beat % 2 == 0:
            self.pianoRollObj.noteUpdate(self.beat)
        self.beat += 1
        self.beat %= PIANOROLL_RESOLUTION

    def playSong(self):
        for p in range(PIANOROLL_PITCH_NUMBER):
            pitch = p + PIANOROLL_LOWEST_NOTE
            if self.pianoRollObj.list[p][self.beat] == NOTELIST_START:
                self.midiPlayer.stopNote(pitch=pitch)
                self.midiPlayer.playNote(pitch=pitch)
            elif self.pianoRollObj.list[p][self.beat] == NOTELIST_PAUSE:
                self.midiPlayer.stopNote(pitch=pitch)

        self.beat += 1
        if self.beat >= PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER:
            self.beat = 0
            self.isPlaying = False
            self.beatTimer.stop()


class PianoRollObj:
    def __init__(self, parent: pianoRollDrawer, logger: logViewerWidget):

        self.parent = parent

        self.list = [[
            0 for _ in range(PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER)
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
            0 for _ in range(PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]
        self.isInputted = False

    def pressingReset(self):
        self.isPressedNotes = [False for _ in range(PIANOROLL_PITCH_NUMBER)]

    def noteUpdate(self, beat):
        for p in range(PIANOROLL_PITCH_NUMBER):
            if self.isPressedNotes[p]:
                if beat == 0 or self.list[p][beat - 1] == 0:
                    self.list[p][beat] = NOTELIST_START
                    self.list[p][beat + 1] = NOTELIST_TIE
                    self.isInputted = True
                else:
                    self.list[p][beat] = NOTELIST_TIE
                    self.list[p][beat + 1] = NOTELIST_TIE

    def getVector(self):
        # print(self.list[0])
        vector = []
        # 単音化リスト
        phoneList = [[
            0 for _ in range(PIANOROLL_RESOLUTION)
        ] for _ in range(PIANOROLL_PITCH_NUMBER)
        ]

        for tick in range(PIANOROLL_RESOLUTION):
            f = False
            for p in reversed(range(PIANOROLL_PITCH_NUMBER)):
                if (self.list[p][tick] != NOTELIST_PAUSE) and not f:
                    phoneList[p][tick] = self.list[p][tick]
                    f = True

        t_ptr = 0
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
                vector.append([p_ptr, (t_ptr - t)])
            else:
                if len(vector) == 0:
                    vector.append([PIANOROLL_PAUSE_NOTEID, 1])
                else:
                    if vector[-1][0] != PIANOROLL_PAUSE_NOTEID:
                        vector.append([PIANOROLL_PAUSE_NOTEID, 1])
                    else:
                        vector[-1][1] += 1
                t_ptr += 1

        return vector

    def geneNotes2List(self, geneNotes):
        tptr = 0
        for note in geneNotes:
            p = note[0] - PIANOROLL_LOWEST_NOTE
            if note[0] != PIANOROLL_PAUSE_NOTEID and tptr >= 16:
                for t in range(note[1]):
                    self.list[p][tptr + t] = NOTELIST_START if t == 0 else NOTELIST_TIE
            tptr += note[1]

    def guess(self, seed_list: list):
        # モデルを利用した推測をここに書く
        self.isGuessed = True
        seed = []
        for pr in seed_list:
            seed.append((min(pr[0] + PIANOROLL_LOWEST_NOTE, PIANOROLL_PAUSE_NOTEID), pr[1]))
        geneData = self.model.generate(seed)
        self.logger.setText(geneData)
        self.geneNotes2List(geneData)
        self.parent.parentObj.parentObj.stop()
