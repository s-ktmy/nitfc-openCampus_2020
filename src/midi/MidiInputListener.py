import pygame.midi
from ..Widget import logViewerWidget
from ..const import *
from .MidiEventController import MidiEventController

class MidiInputListener:

    def __init__(self, drawer: logViewerWidget):
        pygame.init()
        pygame.midi.init()

        # MIDI入力デバイスのチェック
        self.input_id = pygame.midi.get_default_input_id()
        assert self.input_id != -1, "MIDI入力デバイスが認識されていません"
        self.midi_input = pygame.midi.Input(self.input_id)

        self.midi_output = MidiEventController()

        self.drawer = drawer

    def __call__(self):
        # MIDI入力が検知されたら
        if self.midi_input.poll():
            events = self.midi_input.read(MIDIINPUT_ARROW_CHORDS)
            self.drawer.setText(str(events))
            for event in events:
                self.midi_output.send(event[0])

