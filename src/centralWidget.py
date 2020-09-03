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
            pos=QtCore.QRect(10, 10, 701, 461)
        )

        self.logViewerWidget = logViewerWidget(
            parent=self.widget,
            name="logViewer",
            pos=QtCore.QRect(10, 481, 981, 151)
        )

        self.configWidget = configWidget(
            parent=self.widget,
            name="configWidget",
            title="config",
            pos=QtCore.QRect(719, 10, 271, 461)
        )

        self.MidiInputListener = MidiInputListener(drawer=self.logViewerWidget)

        self.midiInputTimer.timeout.connect(self.MidiInputListener)
        self.midiInputTimer.start()
