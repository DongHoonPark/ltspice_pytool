import os
import ltspice
import matplotlib.pyplot as plt

base = os.path.dirname(__file__)
fpfft = f"{base}\\fft.fft"


ltfft = ltspice.Ltspice(fpfft)

ltfft.parse()

vars = ltfft.getVariableNames()
print(f"Variables: {vars}")

