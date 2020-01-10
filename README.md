# LTSpice data parsing library for python

## Installation

```sh
$ pip install ltspice
```

## Usage

```python
import ltspice
filepath = 'Your ltspice output file (.raw)'
l = ltspice.Ltspice(filepath)
l.parse() # Data loading sequence. It may take few minutes.

time = l.getTime()
V1 = l.getData('V(N1)')
```

## Test

### 01 - RC Circuit

#### LTSpice file (.asc)

<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/01_RC/rc.JPG?raw=true" width="500">

#### Python code (.py)

```python
import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'\\rc.raw') 
# Make sure that the .raw file is located in the correct path
l.parse() 

time = l.getTime()
V_source = l.getData('V(source)')
V_cap = l.getData('V(cap)')

plt.plot(time, V_source)
plt.plot(time, V_cap)
plt.show()
```

#### Output result
<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/01_RC_circuit/rc.PNG?raw=true" width="500">

### 02 - Multi point simulation

#### LTSpice file (.asc)
<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/02_Rectifier/rectifier.JPG?raw=true" width="500">

#### Python code (.py)

```python
import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'\\rectifier.raw') 
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

```

#### Output result

```sh
$ [8.299080580472946, 7.855469107627869, 7.391375303268433, 6.944645524024963, 6.529755532741547]

```

<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/02_Rectifier/rectifier.png?raw=true" width="500">

If you want to find more usage examples, please refer the test.md documentation. 

####