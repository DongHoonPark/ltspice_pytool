import ltspice
import matplotlib.pyplot as plt
import numpy as np

l = ltspice.Ltspice('01_RC_circuit.raw') # Make sure that the .raw file is located in the correct path
l.parse() 

time = l.getTime()
V_source = l.getData('V(source)')
V_cap = l.getData('V(cap)')

plt.plot(time, V_source)
plt.plot(time, V_cap)
plt.show()
