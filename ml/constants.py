import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Data parameters; need to reprocess data (run get_data.py) after change.
# Time shift: The 0th index is TIME_SHIFT_INC, the 1st is 2*TIME_SHIFT_INC, etc.
# That is, there is no null time shift.
TIME_SHIFT_INC = 0.01
TIME_SHIFT_COUNT = 100
VELOCITY_COUNT = 32

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
LR = 1
LR_DECAY_FAC = 0.5
LR_DECAY_STEPS = 500
