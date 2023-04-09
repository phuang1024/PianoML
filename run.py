"""
Integration of the model into workflows
i.e. utilities for running the model on an existing midi file.
"""

import argparse

import matplotlib.pyplot as plt
import mido
import numpy as np
import torch
from tqdm import trange

from midi import tokenize_interval
from model import *
from model import args as model_args

PREDICT_LEN = 300


class TemperedSoftmax(torch.nn.Module):
    def __init__(self, temp: float = 1):
        super().__init__()
        self.temp = temp

    def forward(self, x):
        return F.softmax(x * self.temp, dim=-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input MIDI file")
    parser.add_argument("output", help="Output MIDI file")
    args = parser.parse_args()

    midi = mido.MidiFile(args.input)
    src = tokenize_interval(midi, (0, 127))
    src = torch.tensor(src).unsqueeze(1)
    model.load_state_dict(torch.load("model.pt"))
    print(src.shape)

    preds = []
    src_mask = generate_square_subsequent_mask(src.size(0)).to(device)
    sigmoid = TemperedSoftmax(temp=1)
    for _ in trange(PREDICT_LEN):
        output = model(src, src_mask)
        pred = output[-1].squeeze().cpu().detach()
        pred = sigmoid(pred).numpy()

        plt.clf()
        plt.plot(pred)
        plt.pause(.01)

        pred = np.random.choice(128, p=pred)
        #pred[0] *= 0.5
        #pred = np.argmax(pred)
        preds.append(pred)

        src = torch.cat([src, pred * torch.ones(1, 1, dtype=torch.long, device=device)], dim=0)
        src_mask = generate_square_subsequent_mask(src.size(0)).to(device)

    messages = []
    num_zeros = 0
    for pred in preds:
        if pred == 0:
            num_zeros += 1
        else:
            if num_zeros > 0:
                messages.append((0, num_zeros))
            messages.append((pred, 1))
            num_zeros = 0
    print(messages)

    # List of (timestamp, note, on/off (true/false))
    events = []
    count = 0
    for msg in messages:
        events.append((count, msg[0], True))
        count += msg[1]
        events.append((count, msg[0], False))

    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=500000))
    for i, event in enumerate(events):
        time = 0 if i == 0 else event[0] - events[i-1][0]
        time = int(time * model_args.dt * midi.ticks_per_beat * 2)
        type_ = "note_on" if event[2] and event[1] != 0 else "note_off"
        track.append(mido.Message(type=type_, note=event[1], time=time))
        print(track[-1])
    midi.save(args.output)


if __name__ == "__main__":
    main()
