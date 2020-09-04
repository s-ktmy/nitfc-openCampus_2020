import pygame.midi
from ..Widget import pianoRollWidget
from ..const import *
from PyQt5 import QtCore, QtWidgets, QtMultimedia
from pathlib import Path


class MidiEventController:

    def __init__(self, parent: QtWidgets.QWidget, drawer: pianoRollWidget):
        output = pygame.midi.get_default_output_id()
        self.player = pygame.midi.Output(output)
        self.player.set_instrument(MIDIOUTPUT_INSTRUMENTS_ID)

        self.beat = 0
        self.metronome = QtCore.QTimer()
        self.metronome.setInterval(int((1000 * 240 / PIANOROLL_BPM) / 4))
        self.metronome.setSingleShot(False)
        self.metronome.timeout.connect(self.metronomeFunc)

        self.metronome_player = QtMultimedia.QMediaPlayer(parent)
        self.metronome_sound = [
            str(Path("assets/se/metronome_bell.wav").resolve()),
            str(Path("assets/se/metronome_click.wav").resolve())
        ]

    def metronomeFunc(self):
        self.metronome_player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(
            self.metronome_sound[min(self.beat % 4, 1)]
        )))
        self.metronome_player.play()
        self.beat += 1

    def send(self, event: list):
        assert len(event) == EV_INPUT_LENGTH, "不正なMidiイベントデータ"
        pass
        evType, note, velocity, _ = event
        if event[0] == EV_NOTE_ON:
            self.player.note_on(note, velocity)
        if event[0] == EV_NOTE_OFF:
            self.player.note_off(note, velocity)
