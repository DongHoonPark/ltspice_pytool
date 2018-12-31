import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'\\02_Rectifier.raw') 
# Make sure that the .raw file is located in the correct path
l.parse() 

time = l.getTime()
V_source = l.getData('V(source)')
V_cap_max = []

plt.plot(time, V_source)
for i in range(l.c_number): # Iteration in simulation cases 
    time = l.getTime(i)
    # Case number starts from zero
    # Each case has different time point numbers
    V_cap = l.getData('V(cap,pgnd)',i)
    V_cap_max.append(max(V_cap))
    plt.plot(time, V_cap)

print(V_cap_max)

plt.xlim((0, 1e-3))
plt.ylim((-15, 15))
plt.grid()
plt.show()
