import os
import ltspice
import matplotlib.pyplot as plt
import numpy as np

base = os.path.dirname(__file__)
fp = f"{base}\\fft.fft"

lt = ltspice.Ltspice(fp)

lt.parse()
vars = lt.getVariableNames()
print(f"FFT Variables: {vars}")

f = lt.getFrequency()
fig, ax = plt.subplots()


for var in ('V(ip)', 'V(op)'):
    res = 20 * np.log10(np.abs(lt.getData(var)))
    ax.semilogx(f, res, label=var)

fig.legend()
plt.grid()
plt.savefig('fft.png')
plt.show()
