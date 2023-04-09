"""
Utilities for integrating MIDI and transformer.
"""

import os
from threading import Thread

import mido
from tqdm import tqdm

TMPDIR = "/tmp/PianoML"
os.makedirs(TMPDIR, exist_ok=True)


"""
def _process_data(files: list[str]):
    for f in files:
        mid = mido.MidiFile(f)
        tokens = tokenize_midi(mid)
        with open(os.path.join(TMPDIR, os.path.basename(f)), "w") as f:
            f.write("\n".join(map(str, tokens)))

def get_dataset(dir: str):
    files = []
    for f in os.listdir(dir):
        if f.endswith(".mid"):
            files.append(os.path.join(dir, f))

    threads = 16
    thread_files = [files[i::threads] for i in range(threads)]
    threads = [Thread(target=_process_data, args=(f,)) for f in thread_files]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    tokens = []
    for f in files:
        with open(os.path.join(TMPDIR, os.path.basename(f)), "r") as f:
            tokens.append(list(map(int, f.read().splitlines())))
    return tokens
"""


def get_dataset(dir: str, dt: float = 0.1):
    tokens = []
    for file in tqdm(os.listdir(dir), desc="Loading MIDI"):
        if file.endswith(".mid"):
            mid = mido.MidiFile(os.path.join(dir, file))
            tokens += tokenize_midi(mid, dt)
    return tokens


def tokenize_interval(midi: mido.MidiFile, interval, dt: float = 0.1):
    """
    Chop up midi into timestamps of const time (eg 0.1sec) and see which messages play
    at each time.
    Because of the nature of tokens, only one message can be played at each time.
    So, if there are simultaneous messages, the highest one is kept.
    Tokens:
    0: No message
    1-127: Note x on

    :param interval: tuple[int, int]. To make it sane, only consider notes within interval.
    """
    messages = []
    time = 0
    for msg in midi:
        time += msg.time
        if msg.type == "note_on":
            if interval[0] <= msg.note <= interval[1]:
                messages.append((time, msg.note))

    tokens = [0] * int(time/dt + 1)
    ptr = 0
    for i in range(len(tokens)):
        time = i * dt
        while ptr < len(messages) and messages[ptr][0] <= time:
            tokens[i] = max(tokens[i], messages[ptr][1])
            ptr += 1

    return tokens

def filter_tokens(tokens, max_consec=2):
    """
    Remove consecutive zeros that are too long.
    """
    new_tokens = []
    consec = 0
    for token in tokens:
        if token == 0:
            consec += 1
            if consec <= max_consec:
                new_tokens.append(token)
        else:
            consec = 0
            new_tokens.append(token)
    return new_tokens

def tokenize_midi(midi, dt: float = 0.1):
    intervals = (
        (0, 31),
        (16, 47),
        (32, 63),
        (48, 79),
        (64, 95),
        (80, 111),
        (96, 127),
    )
    tokens = []
    for i in intervals:
        tokens += filter_tokens(tokenize_interval(midi, i, dt))
    return tokens


if __name__ == "__main__":
    mid = mido.MidiFile("test.mid")
    print(tokenize_midi(mid))
