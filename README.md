# Ltspice data parsing library for python

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
