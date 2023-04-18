import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Data parameters; need to reprocess data (run get_data.py) after change.
# Time shift: The 0th index is TIME_SHIFT_INC, the 1st is 2*TIME_SHIFT_INC, etc.
# That is, there is no null time shift.
TIME_SHIFT_INC = 0.01
TIME_SHIFT_COUNT = 100
VELOCITY_COUNT = 32
ONEHOT_SIZE = 128 + 128 + TIME_SHIFT_COUNT + VELOCITY_COUNT

# Model hyperparameters
DROPOUT = 0.2
MAX_LEN = 1024
D_MODEL = 512
D_FF = 512
N_HEAD = 4
ENC_LAYERS = 4
DEC_LAYERS = 0

# Training parameters
BATCH_SIZE = 64
SEQ_LEN = 256
EPOCHS = 2
LR = 1
LR_DECAY_FAC = 0.75
LR_DECAY_STEPS = 500
