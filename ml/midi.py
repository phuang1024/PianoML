"""
Utilities for converting from MIDI to messages to tokens.

TODO this doesn't work actually; how do we release notes?

MIDI is stored with mido.MidiFile objects.

Messages are represented with AbsMessage objects.

Tokens follow https://arxiv.org/pdf/1808.03715.pdf
128 + 128 + TIME_SHIFT_COUNT + VELOCITY_COUNT
one-hot
"""

import mido

from constants import *


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

    def __init__(self, note: float = 0, velocity: float = 0, start: float = 0, end: float = 0):
        self.note = int(note)
        self.velocity = float(velocity)
        self.start = float(start)
        self.end = float(end)

    def __repr__(self):
        return f"AbsMessage(note={self.note}, velocity={self.velocity}, start={self.start}, end={self.end})"


def midi_to_msgs(midi: mido.MidiFile):
    starts = [None] * 128
    velocities = [0] * 128
    msgs = []
    time = 0
    for msg in midi:
        time += msg.time
        if msg.type.startswith("note_"):
            if msg.type == "note_on" and msg.velocity > 0:
                starts[msg.note] = time
                velocities[msg.note] = msg.velocity
            else:
                if starts[msg.note] is not None:
                    msgs.append(AbsMessage(msg.note, velocities[msg.note]/127, starts[msg.note], time))
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
    track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
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


def msgs_to_tokens(msgs: list[AbsMessage]) -> list[int]:
    """
    First message is set to time 0
    :return: List of ints. Each is the one-hot index.
    """
    # Temporary (note, velocity, time, on/off True/False)
    # Velocity is 1 to VELOCITY_COUNT
    events = []
    for msg in msgs:
        vel = int(msg.velocity * VELOCITY_COUNT)
        events.append((msg.note, vel, msg.start, True))
        events.append((msg.note, 0, msg.end, False))
    events.sort(key=lambda x: x[2])

    tokens = []
    # 0 to VELOCITY_COUNT
    velocity = None
    # Encoded time is what the time would be, summing all time shift events.
    # We keep this value to correct for cumulative drift.
    # i.e. instead of only looking at curr msg's dt, we look at difference between absolute and encoded time.
    encoded_time = 0
    for i, event in enumerate(events):
        if i > 0:
            # Time shift event.
            delta = event[2] - encoded_time
            mult = int(delta / TIME_SHIFT_INC)
            if mult > 0:
                mult = min(mult, TIME_SHIFT_COUNT)
                tokens.append(128 + 128 + mult)
            encoded_time += mult * TIME_SHIFT_INC

        # Check different velocity.
        if event[3] and velocity != event[1]:
            velocity = event[1]
            tokens.append(128 + 128 + TIME_SHIFT_COUNT + velocity)

        # Note event.
        tokens.append(event[0] if event[3] else event[0] + 128)

    return tokens


def tokens_to_msgs(tokens: list[int]) -> list[AbsMessage]:
    msgs = []
    starts = [None] * 128
    velocities = [0] * 128
    velocity = 0
    time = 0
    for token in tokens:
        if token < 128:
            # Note on.
            starts[token] = time
            velocities[token] = velocity
        elif token < 256:
            # Note off.
            ind = token - 128
            if starts[ind] is not None:
                msgs.append(AbsMessage(ind, velocities[ind], starts[ind], time))
                starts[ind] = None
        elif token < 256 + TIME_SHIFT_COUNT:
            # Time shift.
            time += (token-128-128) * TIME_SHIFT_INC
        else:
            # Velocity.
            velocity = (token-128-128-TIME_SHIFT_COUNT) / VELOCITY_COUNT

    return msgs
