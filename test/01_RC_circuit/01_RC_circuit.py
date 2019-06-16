import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'/01_RC_circuit.raw') 
# Make sure that the .raw file is located in the correct path
l.parse() 

time = l.getTime()
V_source = l.getData('V(source)')
V_cap = l.getData('V(cap)')

plt.plot(time, V_source)
plt.plot(time, V_cap)
plt.xlim((0, 1e-3))
plt.ylim((-10, 10))
plt.grid()
plt.show()
