from PyQt5 import QtWidgets, QtCore
from .Widget import *
from .midi.MidiInputListener import MidiInputListener
from .const import *


class centralWidget:

    def __init__(self, parent: QtWidgets.QMainWindow, name: str):
        self.widget = QtWidgets.QWidget(parent)
        self.widget.setObjectName(name)

        self.midiInputTimer = QtCore.QTimer(parent)
        self.midiInputTimer.setInterval(MIDIINPUT_INTERVAL_TIME)
        self.midiInputTimer.setSingleShot(False)

        self.pianoRollWidget = pianoRollWidget(
            parent=self.widget,
            name="pianoRoll",
            pos=QtCore.QRect(10, 10, 701, 501)
        )

        self.logViewerWidget = logViewerWidget(
            parent=self.widget,
            name="logViewer",
            pos=QtCore.QRect(10, 521, 981, 111)
        )

        self.configWidget = configWidget(
            parent=self.widget,
            name="configWidget",
            title="config",
            pos=QtCore.QRect(719, 10, 271, 501)
        )

        self.startButton = QtWidgets.QPushButton(self.configWidget.widget)
        self.startButton.setGeometry(QtCore.QRect(10, 440, 251, 51))
        self.startButton.setCheckable(True)
        self.startButton.setText("Start")
        self.startButton.clicked.connect(self.play)

        self.MidiInputListener = MidiInputListener(
            parent=self.widget,
            logger=self.logViewerWidget,
            drawer=self.pianoRollWidget
        )

        self.midiInputTimer.timeout.connect(self.MidiInputListener)

    # すべてのタイマーを一斉に動かす
    def play(self):
        self.midiInputTimer.start()
        self.pianoRollWidget.play()
        self.MidiInputListener.play()
