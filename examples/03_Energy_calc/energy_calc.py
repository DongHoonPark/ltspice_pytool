import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'/energy_calc.raw') 
l.parse() 

energy_R1 = []

for i in range(l.case_count): # Iteration in simulation cases
    time = l.get_time(i)
    I_R1 = l.get_data('I(R1)',i)
    R1 = 1
    power_R1 = R1 * I_R1 * I_R1 # Calc dissipated power from R1 from 0 to 5ms
    a = ltspice.integrate(time, power_R1, [0, 5e-3])
    energy_R1.append(a)
    
cond = np.linspace(1e-3, 10e-3, 10) #Simulation condition written in .asc file

plt.xlabel("RL circuit inductance (H)")
plt.ylabel("Energy (J)")
plt.grid()
plt.plot(cond, energy_R1)
plt.savefig('energy_calc.png')
plt.show()