import matplotlib.pyplot as plt
import numpy as np


data = open("results/log.txt", "r").read().strip().split("\n")
data = list(map(float, data))
data = np.array(data)
plt.plot(data)
plt.show()
