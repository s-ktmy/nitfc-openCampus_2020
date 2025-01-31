# 定数の定義

# === コンフィグ的な定数 === #

# pianoRollWidget 描画更新速度[ms]
PIANOROLL_UPDATE_TIME = 20

# MidiInput 入力インターバル[ms]
MIDIINPUT_INTERVAL_TIME = 20

# MidiInput 同時押し許可数
MIDIINPUT_ARROW_CHORDS = 10

# logViewerWidget 行数
LOG_ROW_NUMBER = 100

# MidiEventController 鳴らす音の種類
MIDIOUTPUT_INSTRUMENTS_ID = 0

# PianoRoll ピッチ数
PIANOROLL_PITCH_NUMBER = 49

# PianoRoll 小節数
PIANOROLL_MEASURE_NUMBER = 4

# PianoRoll 分解能
PIANOROLL_RESOLUTION = 16

# PianoRoll BPM
PIANOROLL_BPM = 60

# PianoRoll 最低音のピッチ番号
PIANOROLL_LOWEST_NOTE = 48

# PianoRoll オブジェクトサイズ[x,y]
PIANOROLL_OBJ_SIZE = [10, 10]

# PianoRoll 起点座標
PIANOROLL_BASE_POS = [61, 488]

# ピアノロール 休符のノート番号
PIANOROLL_PAUSE_NOTEID = 256

# RNN 生成する小節数
RNN_GENERATE_MEASURE = 3

# === システム的な定数 === #

# MIDIイベントに関する定数
# ノートオンEv定数
EV_NOTE_ON = 144
# ノートオフEv定数
EV_NOTE_OFF = 128

# MIDI入力イベントの要素数
EV_INPUT_LENGTH = 4

# pianoRoll noteListに関する定数
NOTELIST_PAUSE = 0
NOTELIST_START = 1
NOTELIST_TIE = 2

# pianoRoll X方向の長さ
PIANOROLL_X_LENGTH = PIANOROLL_RESOLUTION * PIANOROLL_MEASURE_NUMBER * PIANOROLL_OBJ_SIZE[0]


