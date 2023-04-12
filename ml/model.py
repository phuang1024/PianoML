import torch

from constants import *


def create_model():
    return torch.nn.Transformer(
        d_model=D_MODEL,
        nhead=N_HEAD,
        num_encoder_layers=ENC_LAYERS,
        num_decoder_layers=DEC_LAYERS,
        dim_feedforward=D_FF,
        batch_first=True,
        dropout=DROPOUT,
    ).to(DEVICE)
