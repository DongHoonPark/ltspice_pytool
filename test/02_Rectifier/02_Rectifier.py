import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'\\02_Rectifier.raw') 
# Make sure that the .raw file is located in the correct path
l.parse() 

time = l.getTime()
V_source = l.getData('V(source)')


plt.plot(time, V_source)
for i in range(l.c_number): # Iteration in simulation cases 
    time = l.getTime(i)
    V_cap = l.getData('V(cap,pgnd)',i)
    plt.plot(time, V_cap)

plt.xlim((0, 1e-3))
plt.ylim((-15, 15))
plt.grid()
plt.show()
