import matplotlib.pyplot as plt
import numpy as np


data = open("log.txt", "r").read().strip().split("\n")
data = list(map(float, data))
data = np.array(data)
plt.plot(data)
plt.show()
