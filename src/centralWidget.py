from PyQt5 import QtWidgets, QtCore
from .Widget import *
from .midi.MidiInputListener import MidiInputListener
from .const import *


class centralWidget:

    def __init__(self, parent: QtWidgets.QMainWindow, name: str):
        self.widget = QtWidgets.QWidget(parent)
        self.widget.setObjectName(name)

        self.logViewerWidget = logViewerWidget(
            parent=self.widget,
            name="logViewer",
            pos=QtCore.QRect(10, 521, 981, 111)
        )

        self.pianoRollWidget = pianoRollWidget(
            parent=self.widget,
            parentObj=self,
            name="pianoRoll",
            pos=QtCore.QRect(10, 10, 701, 501),
            logger=self.logViewerWidget
        )

        self.configWidget = configWidget(
            parent=self.widget,
            name="configWidget",
            title="config",
            pos=QtCore.QRect(719, 10, 271, 501),
            logger=self.logViewerWidget
        )

        self.MidiInputListener = MidiInputListener(
            parent=self.widget,
            logger=self.logViewerWidget,
            drawer=self.pianoRollWidget
        )

        self.midiInputTimer = QtCore.QTimer(parent)
        self.midiInputTimer.setInterval(MIDIINPUT_INTERVAL_TIME)
        self.midiInputTimer.setSingleShot(False)

        self.midiInputTimer.timeout.connect(self.MidiInputListener)

        self.pianoRollWidget.setMidiPlayer(self.MidiInputListener.midi_output)

        self.startButton = QtWidgets.QPushButton(self.configWidget.widget)
        self.startButton.setGeometry(QtCore.QRect(10, 440, 251, 51))
        self.startButton.setCheckable(True)
        self.startButton.setText("Start")
        self.startButton.clicked.connect(self.onPushedStartButton)

        self.startButton = QtWidgets.QPushButton(self.configWidget.widget)
        self.startButton.setGeometry(QtCore.QRect(10, 370, 251, 51))
        self.startButton.setCheckable(True)
        self.startButton.setText("Play")
        self.startButton.clicked.connect(self.onPushedPlayButton)

    # すべてのタイマーを一斉に動かす
    def play(self):
        self.midiInputTimer.start()
        self.pianoRollWidget.play()
        self.MidiInputListener.play()

    # すべてのタイマーを一斉に止める
    def stop(self):
        self.midiInputTimer.stop()
        self.pianoRollWidget.stop()
        self.MidiInputListener.stop()

    def onPushedStartButton(self):
        self.stop()
        self.play()

    def onPushedPlayButton(self):
        self.pianoRollWidget.songPlay()
