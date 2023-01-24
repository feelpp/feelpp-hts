import matplotlib.pyplot as plt
import numpy as np

from math import erf

# plt.style.use('_mpl-gallery')

# make data
x = np.linspace(-10, 10, 10001)
y = [ erf(t) for t in x]

# plot
# fig, ax = plt.subplots()

# ax.plot(x, y, linewidth=2.0, marker='o')

with open('erf.csv', 'w') as f:
    f.write('X,Erf\n')
    t = 1.e-10
    f.write(f'{t},{erf(t)}\n')
    t = -1.e-10
    f.write(f'{t},{erf(t)}\n')
    for t in x:
        f.write(f'{t},{erf(t)}\n')
    t = 1.e+10
    f.write(f'{t},{erf(t)}\n')
    t = -1.e+10
    f.write(f'{t},{erf(t)}\n')
    
# plt.show()
