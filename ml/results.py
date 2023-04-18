import argparse

import matplotlib.pyplot as plt
import torch

from model import *
from utils import *


def load_latest_model(runs_dir):
    model = Model().to(DEVICE)
    path = get_last_model(get_last_run(runs_dir))
    model.load_state_dict(torch.load(path))
    return model


def run_model(model, data, length):
    """
    :param data: Sequence of tokens.
    """
    data = torch.tensor(data, dtype=torch.long, device=DEVICE).view(1, -1)
    orig_len = data.size(1)
    model.eval()
    with torch.no_grad():
        for i in range(length):
            output = model(data, data[:, orig_len+i-1:])

            plt.plot(output[0, -1].cpu().numpy())
            plt.savefig("/tmp/a.png")

            _, next_word = torch.max(output[:, -1], dim=1)
            data = torch.cat((data, next_word.view(1, 1)), dim=1)

    output = data[0, orig_len:].tolist()
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data", help="Path to data directory")
    parser.add_argument("--runs", default="runs", help="Path to tensorboard runs directory")
    args = parser.parse_args()

    model = load_latest_model(args.runs)


if __name__ == "__main__":
    main()
