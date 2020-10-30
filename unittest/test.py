import unittest
from ltspice import Ltspice
import os
from os import path


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
            Ltspice(path.join(__filepath, 'rl_circuit_fftascii.fft')).parse()
        except Exception as e:
            print(e)
            passed = False

        self.assertTrue(passed)

if __name__ == '__main__':
    unittest.main()