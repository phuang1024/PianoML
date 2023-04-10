import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Validation data
data = pd.read_csv("results/logval.csv")
f = plt.figure(1)
plt.title("Validation loss")
plt.plot(np.arange(len(data)), data["loss"], label="Validation loss")

# Training data
data = pd.read_csv("results/logtrain.csv")

f = plt.figure(2)
plt.title("Training loss")
x = np.arange(len(data))
plt.plot(x, data["loss"], label="Training loss")

f = plt.figure(3)
plt.title("Learning rate")
plt.plot(x, data["lr"], label="lr")

plt.legend()
plt.show()
