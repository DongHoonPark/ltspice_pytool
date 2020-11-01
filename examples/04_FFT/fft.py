import os
import ltspice
import matplotlib.pyplot as plt
import numpy as np

base = os.path.dirname(__file__)
fp = f"{base}\\fft.fft"

l = ltspice.Ltspice(fp)

l.parse()
vars = l.variables
print(f"FFT Variables: {vars}")

f = l.get_frequency()
fig, ax = plt.subplots()


for var in ('V(ip)', 'V(op)'):
    res = 20 * np.log10(np.abs(l.get_data(var)))
    ax.semilogx(f, res, label=var)

fig.legend()
plt.grid()
plt.savefig('fft.png')
plt.show()
