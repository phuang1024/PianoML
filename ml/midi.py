"""
Utilities for integrating MIDI and transformer.
"""

import os
from multiprocessing import Process

import mido
import torch
from tqdm import tqdm

DT = 0.12
THREADS = 32
TMPDIR = "/tmp/PianoML"
os.makedirs(TMPDIR, exist_ok=True)


def get_dataset_worker(jobs, dt):
    for file in jobs:
        mid = mido.MidiFile(file)
        tokens = tokenize_midi(mid, dt)
        tokens = torch.tensor(tokens, dtype=torch.uint8)
        out_file = os.path.join(TMPDIR, os.path.basename(file))
        torch.save(tokens, out_file)

def get_dataset(dir: str, dt: float = DT) -> torch.Tensor:
    files = []
    for file in os.listdir(dir):
        if file.endswith(".mid"):
            files.append(os.path.join("data", file))

    threads = []
    for i in range(THREADS):
        t = Process(target=get_dataset_worker, args=(files[i::THREADS], dt))
        threads.append(t)
        t.start()

    pbar = tqdm(total=len(files), desc="Processing MIDI")
    while any(t.is_alive() for t in threads):
        num_done = len(os.listdir(TMPDIR))
        pbar.update(num_done - pbar.n)
    pbar.close()

    all_data = []
    for file in os.listdir(TMPDIR):
        all_data.append(torch.load(os.path.join(TMPDIR, file)))
    return torch.cat(all_data)


def tokenize_interval(midi: mido.MidiFile, interval, dt: float = DT):
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

def tokenize_midi(midi, dt: float = DT):
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


def events_to_midi(events):
    """
    :param events: List of (timestamp, note, on/off (true/false))
    """
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=500000))
    for i, event in enumerate(events):
        time = 0 if i == 0 else event[0] - events[i-1][0]
        time = int(time * midi.ticks_per_beat * 2)
        type_ = "note_on" if event[2] and event[1] != 0 else "note_off"
        print(type_, event[1], time)
        track.append(mido.Message(type=type_, note=event[1], time=time))
    return midi


if __name__ == "__main__":
    data = get_dataset("data", 0.12)
    torch.save(data, "results/all_data.pt")
