"""
Utilities for converting from MIDI to messages to tokens.

TODO this doesn't work actually; how do we release notes?

MIDI is stored with mido.MidiFile objects.
Messages are represented with AbsMessage objects.
Tokens are arrays of length 257 (128 + 128 + 1):
- First 128 is probability of note i playing.
- Second 128 is velocity of each note.
- Last is time after previous chord.
"""

import mido


class AbsMessage:
    """
    Message with absolute start and end times.
    """
    note: int
    # Interpolate 0-127 to 0-1.
    velocity: float
    # Start and end are absolute timestamps in seconds.
    start: float
    end: float

    def __init__(self, note=0, velocity=0, start=0, end=0):
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end = end

    def __repr__(self):
        return f"AbsMessage(note={self.note}, velocity={self.velocity}, start={self.start}, end={self.end})"


def midi_to_msgs(midi: mido.MidiFile):
    starts = [None] * 128
    msgs = []
    for msg in midi:
        if msg.type == "note_on":
            starts[msg.note] = msg.time
        elif msg.type == "note_off":
            if starts[msg.note] is not None:
                msgs.append(AbsMessage(msg.note, msg.velocity/127, starts[msg.note], msg.time))
                starts[msg.note] = None

    return msgs


def msgs_to_midi(msgs: list[AbsMessage], ticks_per_beat=480):
    # Temporary list of (note, velocity, time, on/off True/False)
    events = []
    for msg in msgs:
        events.append((msg.note, msg.velocity, msg.start, True))
        events.append((msg.note, 0, msg.end, False))
    events.sort(key=lambda x: x[2])

    midi = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    for i, event in enumerate(events):
        dt = 0 if i == 0 else events[i][2] - events[i-1][2]
        ticks = int(dt * ticks_per_beat * 2)
        track.append(mido.Message(
            type="note_on" if event[3] else "note_off",
            note=event[0],
            velocity=int(event[1] * 127),
            time=ticks,
        ))

    return midi


def msgs_to_tokens(msgs: list[AbsMessage], threshold: float = 0.05):
    """
    :param threshold: Messages closer than this are considered one concurrent chord.
        Message start time is used.
    """
    groups = []
    start_i = None
