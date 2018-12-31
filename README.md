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

<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/01_RC_circuit/01_RC_circuit.JPG?raw=true" width="500">

#### Python code (.py)

```python
import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os

l = ltspice.Ltspice(os.path.dirname(__file__)+'\\01_RC_circuit.raw') 
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
<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/01_RC_circuit/01_RC_circuit.PNG?raw=true" width="500">

### 02 - Multi point simulation

#### LTSpice file (.asc)
<img src="https://github.com/DongHoonPark/ltspice_pytool/blob/master/test/02_Rectifier/02_Rectifier.JPG?raw=true" width="500">