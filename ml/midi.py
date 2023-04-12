"""
Utilities for converting from MIDI to messages to tokens.

TODO this doesn't work actually; how do we release notes?

MIDI is stored with mido.MidiFile objects.
Messages are represented with AbsMessage objects.
Tokens are arrays of length 131 (128 + 3), each representing one message.
- First 128 is probability of note i playing. Choose highest.
- Next 2 is start, end, in absolute seconds.
- Last is velocity, in 0-1.
"""

import mido

import torch


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
        self.note = int(note)
        self.velocity = float(velocity)
        self.start = float(start)
        self.end = float(end)

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


def msgs_to_tokens(msgs: list[AbsMessage]) -> torch.Tensor:
    """
    :return: Shape (num_msgs, 131)
    """
    tokens = torch.zeros((len(msgs), 131))
    for i, msg in enumerate(msgs):
        tokens[i, msg.note] = 1
        tokens[i, 128] = msg.start
        tokens[i, 129] = msg.end
        tokens[i, 130] = msg.velocity
    return tokens


def tokens_to_msgs(tokens: torch.Tensor) -> list[AbsMessage]:
    """
    Highest probability note is picked.
    """
    msgs = []
    for i in range(tokens.size(0)):
        note = torch.argmax(tokens[i, :128])
        start = tokens[i, 128]
        end = tokens[i, 129]
        velocity = tokens[i, 130]
        msgs.append(AbsMessage(note, velocity, start, end))
    return msgs
