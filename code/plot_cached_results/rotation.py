import os
from toolkit import toolkit
import matplotlib.pyplot as plt
import numpy as np


def gauss_monte_carlo():
    x = []
    for i in range(1000000):
        y = np.abs(np.random.normal(size=35))
        x.append((np.array(np.mean(y)), np.array(np.std(y))))
    x = np.array(x)
    print(x)
    print((np.mean(x[:, 0]), np.std(x[:, 0])))
    print((np.mean(x[:, 1]), np.std(x[:, 1])))


#gauss_monte_carlo()

toolkit.plt_use_tex()
fig = plt.figure()
ax = fig.add_subplot()

folders = ["./rotations/act/", "./rotations/planck/"]
labels = ["ACT", "Planck"]

NSIDES = np.array((1, 2, 4, 8, 16, 32, 64, 128))
x = np.append(np.array(1/2), NSIDES)

y = np.zeros((len(folders), len(x)))
y_std = np.zeros((len(folders), len(x)))

for folder in folders:
    files = os.listdir(folder)
    sigma = np.zeros((len(files), len(x)))
    for file in files:
        data = np.load(folder + file)[0]
        sigma[files.index(file)] = np.abs(data[0] / data[1])
    for i in range(len(y[0])):
        y[folders.index(folder)][i] = np.mean(sigma[:, i])
        y_std[folders.index(folder)][i] = np.std(sigma[:, i])
print(y, y_std)

for i in range(len(folders)):
    plt.errorbar(x, y[i], y_std[i], label=labels[i])

plt.plot((1/2, np.max(NSIDES)), (0.8, 0.8), color="k", linestyle="dashed")
plt.plot((1/2, np.max(NSIDES)), (0.2, 0.2), color="k", linestyle="dotted")
plt.plot((1/2, np.max(NSIDES)), (1.4, 1.4), color="k", linestyle="dotted")

plt.xscale("log")
plt.legend()
ax.set_xticks(x, ["C"] + list(NSIDES))
plt.savefig("test.pdf")
plt.show()
