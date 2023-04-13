import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model hyperparameters
DROPOUT = 0.1
MAX_LEN = 5000
D_MODEL = 256
D_FF = 256
N_HEAD = 2
ENC_LAYERS = 4
DEC_LAYERS = 4

# Training parameters
BATCH_SIZE = 128
SEQ_LEN = 64
EPOCHS = 5
