import os

import matplotlib.pyplot as plt
import numpy as np
import torch

DT = (0.5, 0.25, 0.125, 0.0625)
NETSIZE = (64, 128, 256, 512, 1024)


def exp_dt():
    for i in DT:
        print(f"@@@@@@@@ dt = {i} @@@@@@@@@")
        os.system(f"python model.py --dt {i}")
        os.system(f"mv log.txt log_{i}.txt")

def plot_dt():
    for i in DT:
        with open(f"log_{i}.txt") as f:
            vals = map(float, f.read().strip().split("\n"))
            vals = np.array(list(vals))
            plt.plot(vals, label=f"dt = {i}")
    plt.legend()
    plt.show()


def exp_netsize():
    for i in NETSIZE:
        print(f"@@@@@@@@ netsize = {i} @@@@@@@@@")
        os.system(f"python model.py --netsize {i}")
        os.system(f"mv log.txt log_{i}.txt")

def plot_netsize():
    for i in NETSIZE:
        with open(f"log_{i}.txt") as f:
            vals = map(float, f.read().strip().split("\n"))
            vals = np.array(list(vals))
            plt.plot(vals, label=f"netsize = {i}")
    plt.legend()
    plt.show()


def plot_data():
    data = torch.load("all_data.pt")
    plot = np.empty((128,), dtype=int)
    for i in range(128):
        plot[i] = (data == i).sum()
    plt.plot(plot)
    plt.show()


if __name__ == "__main__":
    plot_data()
