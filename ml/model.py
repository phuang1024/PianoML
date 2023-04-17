import os

import torch
import torch.nn as nn
from torch.utils.data import Dataset

from constants import *


class TokenDataset(Dataset):
    def __init__(self, directory):
        self.files = [f for f in os.listdir(directory) if f.endswith(".pt")]
        self.files = [os.path.join(directory, f) for f in self.files]

        total_size = 0
        for f in self.files:
            total_size += torch.load(f).numel()

        self.tokens = torch.zeros((total_size,), dtype=torch.int16)
        ind = 0
        for f in self.files:
            curr_tokens = torch.load(f)
            curr_len = curr_tokens.numel()
            self.tokens[ind:ind+curr_len] = curr_tokens
            ind += curr_len
        self.tokens = self.tokens.to(torch.long)

        self.length = (len(self.tokens)-1) // SEQ_LEN
        self.onehot_size = 256 + TIME_SHIFT_COUNT + VELOCITY_COUNT
        self.tokens = torch.clip(self.tokens, 0, self.onehot_size-1)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        i = idx * SEQ_LEN
        x = self.tokens[i : i+SEQ_LEN]
        y = self.tokens[i+1 : i+SEQ_LEN+1]
        x_oh = torch.nn.functional.one_hot(x, self.onehot_size)
        y_oh = torch.nn.functional.one_hot(y, self.onehot_size)
        return x_oh, y_oh


class Model(nn.Module):
    def __init__(self):
        super().__init__()

        self.input = nn.Sequential(
            nn.Linear(131, D_FF),
            nn.ReLU(),
            nn.Linear(D_FF, D_MODEL),
        )
        self.transformer = nn.Transformer(
            d_model=D_MODEL,
            nhead=N_HEAD,
            num_encoder_layers=ENC_LAYERS,
            num_decoder_layers=DEC_LAYERS,
            dim_feedforward=D_FF,
            batch_first=True,
            dropout=DROPOUT,
        )
        self.output = nn.Sequential(
            nn.Linear(D_MODEL, 131),
        )

    def forward(self, x, y):
        x = self.input(x)
        y = self.input(y)
        x = self.transformer(x, y)
        x = self.output(x)
        return x
