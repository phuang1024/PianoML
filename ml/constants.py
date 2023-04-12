import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model hyperparameters
DROPOUT = 0.1
MAX_LEN = 5000
D_MODEL = 64
D_FF = 256
N_HEAD = 2
ENC_LAYERS = 4
DEC_LAYERS = 4
