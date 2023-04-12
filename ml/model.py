"""
Implementation of Attention is All You Need.
"""

import math

import torch
import torch.nn as nn

from constants import *


class PositionalEncoding(nn.Module):
    """
    Exponentially increasing sinusoidal additive positional encoding.
    """

    pe: torch.Tensor

    def __init__(self):
        super().__init__()
        self.dropout = nn.Dropout(p=DROPOUT)

        position = torch.arange(MAX_LEN).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, D_EM, 2) * (-math.log(10000.0) / D_EM))
        pe = torch.zeros(1, MAX_LEN, D_EM)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        :param x: Tensor shape (bs, seq_len, D_EM)
        """
        x = x + self.pe[:, :x.size(1), :]
        x = self.dropout(x)
        return x

