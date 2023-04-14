import torch
import torch.nn as nn
from torch.utils.data import Dataset

from constants import *


class TokenDataset(Dataset):
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = torch.load(data_path)
        self.length = len(self.data) // SEQ_LEN

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        i = idx * SEQ_LEN
        x = self.data[i : i+SEQ_LEN]
        y = self.data[i+1 : i+SEQ_LEN+1]
        return x, y


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
