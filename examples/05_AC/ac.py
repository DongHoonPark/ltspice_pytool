import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__) + '/ac.raw')
l.parse()

fig, axes = plt.subplots(2, 1, figsize=(7,7))

labels = list(map(lambda x: "Rmax = {}kOhm".format(str(x)), np.linspace(9, 11, 3).astype(int)))

for case in range(l.case_count):
    freq = l.get_frequency(case)
    V_out = l.get_data('V(Vout)', case)

    Vout_amplitude = 20 * np.log10(np.abs(V_out))
    Vout_angle = np.angle(V_out, deg=True)

    axes[0].semilogx(freq, Vout_amplitude)
    axes[1].semilogx(freq, Vout_angle, label=labels[case])

axes[0].grid()
axes[1].grid()
axes[1].set_xlabel("Frequency (Hz)")
axes[0].set_ylabel("Amplitude (dB)")
axes[1].set_ylabel("Phase (Deg)")
plt.savefig("ac.png")
plt.legend()
plt.show()