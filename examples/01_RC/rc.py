import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'/rc.raw') 
l.parse() 

time = l.get_time()
V_source = l.get_data('V(source)')
V_cap = l.get_data('V(cap)')

plt.plot(time, V_source)
plt.plot(time, V_cap)
plt.xlim((0, 1e-3))
plt.ylim((-10, 10))
plt.grid()
plt.savefig("rc.png")
plt.show()
