import pygame.midi
from ..const import *


class MidiEventController:

    def __init__(self):
        self.player = pygame.midi.Output(pygame.midi.get_default_output_id())
        self.player.set_instrument(MIDIOUTPUT_INSTRUMENTS_ID)

    def send(self, event: list):
        assert len(event) == EV_INPUT_LENGTH, "不正なMidiイベントデータ"
        evType, note, velocity, _ = event
        if event[0] == EV_NOTE_ON:
            self.player.note_on(note, velocity)
        if event[0] == EV_NOTE_OFF:
            self.player.note_off(note, velocity)
