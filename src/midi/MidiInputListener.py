import pygame.midi
from ..Widget import logViewerWidget, pianoRollWidget
from ..const import *
from .MidiEventController import MidiEventController
from PyQt5 import QtWidgets


class MidiInputListener:

    def __init__(self, parent: QtWidgets.QWidget, drawer: pianoRollWidget, logger: logViewerWidget):
        pygame.init()
        pygame.midi.init()

        # MIDI入力デバイスのチェック
        self.input_id = pygame.midi.get_default_input_id()
        assert self.input_id != -1, "MIDI入力デバイスが認識されていません"
        self.midi_input = pygame.midi.Input(self.input_id)

        self.midi_output = MidiEventController(parent, drawer)

        self.logger = logger

    def __call__(self):
        # MIDI入力が検知されたら
        if self.midi_input.poll():
            events = self.midi_input.read(MIDIINPUT_ARROW_CHORDS)
            self.logger.setText(str(events))
            for event in events:
                self.midi_output.send(event[0])

    def play(self):
        self.flush()
        self.midi_output.metronome.start()
        self.midi_output.metronomeFunc()

    def flush(self):
        while len(self.midi_input.read(128)) != 0:
            pass
