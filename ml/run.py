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

from midi import tokenize_interval, events_to_midi, DT
from model import *


class TemperedSoftmax(torch.nn.Module):
    def __init__(self, temp: float = 1):
        super().__init__()
        self.temp = temp

    def forward(self, x):
        return F.softmax(x * self.temp, dim=-1)


def main(input_path, output_path, length):
    midi = mido.MidiFile(input_path)
    src = tokenize_interval(midi, (0, 127))
    src = torch.tensor(src, device=device).unsqueeze(1)
    model.load_state_dict(torch.load("results/model.pt"))
    print(src.shape)

    preds = []
    src_mask = generate_square_subsequent_mask(src.size(0)).to(device)
    sigmoid = TemperedSoftmax(temp=1)
    for _ in trange(length):
        output = model(src, src_mask)
        pred = output[-1].squeeze().cpu().detach()
        pred = sigmoid(pred).numpy()

        """
        plt.clf()
        plt.plot(pred)
        plt.pause(.01)
        """

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
        events.append((DT*count, msg[0], True))
        count += msg[1]
        events.append((DT*count, msg[0], False))

    midi = events_to_midi(events)
    midi.save(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input MIDI file")
    parser.add_argument("output", help="Output MIDI file")
    parser.add_argument("--length", default=16, type=int)
    args = parser.parse_args()
    main(args.input, args.output, args.length)
