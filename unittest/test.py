import unittest
from ltspice import Ltspice
import os
from os import path
import numpy as np

class TestLtspiceMethods(unittest.TestCase):

    def test_loading(self):
        __filepath = os.path.dirname(__file__)
        passed = True
        try:
            Ltspice(path.join(__filepath, 'rl_circuit_tran.raw')).parse()
            Ltspice(path.join(__filepath, 'rl_circuit_tran64b.raw')).set_variable_dtype(float).parse()
            Ltspice(path.join(__filepath, 'rl_circuit_ac.raw')).parse()
            Ltspice(path.join(__filepath, 'rl_circuit_fft.fft')).parse()
            Ltspice(path.join(__filepath, 'rl_circuit_tranascii.raw')).parse()
            Ltspice(path.join(__filepath, 'rl_circuit_acascii.raw')).parse()
            Ltspice(path.join(__filepath, 'rl_circuit_fftascii.fft')).parse()
        except Exception as e:
            print(e)
            passed = False

        self.assertTrue(passed)

    def test_transient_data(self):
        __filepath = os.path.dirname(__file__)
        lt1 = Ltspice(path.join(__filepath, 'rl_circuit_tran.raw')).parse()
        lt2 = Ltspice(path.join(__filepath, 'rl_circuit_tran64b.raw')).set_variable_dtype(float).parse()
        lt3 = Ltspice(path.join(__filepath, 'rl_circuit_tranascii.raw')).parse()

        self.assertTrue(abs(lt1.get_data('V(R1)', time=0.1) - lt2.get_data('V(R1)', time=0.1)) < 2e-3)
        self.assertTrue(abs(lt2.get_data('V(R1)', time=0.1) - lt3.get_data('V(R1)', time=0.1)) < 2e-3)
        self.assertTrue(abs(lt3.get_data('V(R1)', time=0.1) - lt1.get_data('V(R1)', time=0.1)) < 2e-3)

    def test_fft_data(self):
        __filepath = os.path.dirname(__file__)
        lt1 = Ltspice(path.join(__filepath, 'rl_circuit_fft.fft')).parse()
        lt2 = Ltspice(path.join(__filepath, 'rl_circuit_fftascii.fft')).parse()
        freq = np.linspace(1000, 130000, 130)
        x1 = lt1.get_data('V(R1)')
        x2 = lt2.get_data('V(R1)')
        err = np.abs((x1 - x2) / (x1.max() - x1.min()))
        self.assertTrue(err.max() < 0.01)

    def test_ac_data(self):
        __filepath = os.path.dirname(__file__)
        lt1 = Ltspice(path.join(__filepath, 'rl_circuit_acascii.raw')).parse()
        pass



if __name__ == '__main__':
    unittest.main()

