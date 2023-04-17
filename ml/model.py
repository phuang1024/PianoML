import math
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
        self.tokens = torch.clip(self.tokens, 0, ONEHOT_SIZE-1)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        i = idx * SEQ_LEN
        x = self.tokens[i : i+SEQ_LEN]
        y = self.tokens[i+1 : i+SEQ_LEN+1]
        #x_oh = torch.nn.functional.one_hot(x, ONEHOT_SIZE)
        #y_oh = torch.nn.functional.one_hot(y, ONEHOT_SIZE)
        return x, y


class PositionalEncoding(nn.Module):
    """
    From https://pytorch.org/tutorials/beginner/transformer_tutorial.html
    """

    def __init__(self):
        super().__init__()
        self.dropout = nn.Dropout(p=DROPOUT)

        position = torch.arange(SEQ_LEN).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, D_MODEL, 2) * (-math.log(10000) / D_MODEL))
        pe = torch.zeros(1, SEQ_LEN, D_MODEL)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


class Model(nn.Module):
    def __init__(self):
        super().__init__()

        self.embedding = nn.Embedding(ONEHOT_SIZE, D_MODEL)
        self.pe = PositionalEncoding()
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
            nn.Linear(D_MODEL, ONEHOT_SIZE),
            nn.Sigmoid(),
        )

    def forward(self, x, y):
        x = self.embedding(x) * math.sqrt(D_MODEL)
        x = self.pe(x)
        y = self.embedding(y) * math.sqrt(D_MODEL)
        y = self.pe(y)

        mask = self.transformer.generate_square_subsequent_mask(y.size(1)).to(DEVICE)
        x = self.transformer(x, y, tgt_mask=mask)
        x = self.output(x)

        return x
