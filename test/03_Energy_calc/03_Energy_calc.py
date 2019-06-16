import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'/03_Energy_calc.raw') 
# Make sure that the .raw file is located in the correct path
l.parse() 

energy_R1 = []

for i in range(l.c_number): # Iteration in simulation cases 
    time = l.getTime(i)
    I_R1 = l.getData('I(R1)',i)
    R1 = 1
    power_R1 = R1 * I_R1 * I_R1 # Calc dissipated power from R1 from 0 to 0.5s
    a = ltspice.integrate(time, power_R1, [0, 0.5])
    energy_R1.append(a)
    
cond = np.linspace(1e-3, 10e-3, 10) #Simulation condition written in .asc file

plt.plot(cond, energy_R1)
plt.show()
    