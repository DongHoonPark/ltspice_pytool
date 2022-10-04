import unittest
from ltspice import Ltspice
import os
from os import path
import numpy as np

class TestLtspiceMethods(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self.__file_path = os.path.dirname(__file__)

    def test_loading(self):
        passed = True
        try:
            Ltspice(path.join(self.__file_path, 'rl_circuit_tran.raw')).parse()
            Ltspice(path.join(self.__file_path, 'rl_circuit_tran64b.raw')).parse()
            Ltspice(path.join(self.__file_path, 'rl_circuit_ac.raw')).parse()
            Ltspice(path.join(self.__file_path, 'rl_circuit_fft.fft')).parse()
            Ltspice(path.join(self.__file_path, 'rl_circuit_tranascii.raw')).parse()
            Ltspice(path.join(self.__file_path, 'rl_circuit_acascii.raw')).parse()
            Ltspice(path.join(self.__file_path, 'rl_circuit_fftascii.fft')).parse()
        except Exception as e:
            print(e)
            passed = False

        self.assertTrue(passed)

    def test_transient_data(self):
        lt1 = Ltspice(path.join(self.__file_path, 'rl_circuit_tran.raw')).parse()
        lt2 = Ltspice(path.join(self.__file_path, 'rl_circuit_tran64b.raw')).parse()
        lt3 = Ltspice(path.join(self.__file_path, 'rl_circuit_tranascii.raw')).parse()

        self.assertTrue(abs(lt1.get_data('V(R1)', time=0.1) - lt2.get_data('V(R1)', time=0.1)) < 2e-3)
        self.assertTrue(abs(lt2.get_data('V(R1)', time=0.1) - lt3.get_data('V(R1)', time=0.1)) < 2e-3)
        self.assertTrue(abs(lt3.get_data('V(R1)', time=0.1) - lt1.get_data('V(R1)', time=0.1)) < 2e-3)

        t1 = lt1.get_x()
        tp_last = 0
        for tp in t1:
            self.assertLessEqual(tp_last, tp)
            tp_last = tp
        
        t2 = lt2.get_x()
        tp_last = 0
        for tp in t2:
            self.assertLessEqual(tp_last, tp)
            tp_last = tp
   
        t3 = lt3.get_x()
        tp_last = 0
        for tp in t3:
            self.assertLessEqual(tp_last, tp)
            tp_last = tp

    def test_fft_data(self):
        lt1 = Ltspice(path.join(self.__file_path, 'rl_circuit_fft.fft')).parse()
        lt2 = Ltspice(path.join(self.__file_path, 'rl_circuit_fftascii.fft')).parse()
        
        freq = np.linspace(1000, 130000, 130)
        
        x1 = lt1.get_data('V(R1)', frequency=freq)
        x2 = lt2.get_data('V(R1)', frequency=freq)
        
        self.assertTrue(np.isclose(0, np.max(abs(x1) -abs(x2)), atol=1e-5))
        self.assertTrue(np.isclose(0, np.max(np.angle(x1) - np.angle(x2)), atol=1e-2))

    def test_ac_data(self):
        lt1 = Ltspice(path.join(self.__file_path, 'rl_circuit_acascii.raw')).parse()
        lt2 = Ltspice(path.join(self.__file_path, 'rl_circuit_ac.raw')).parse()

        freq = np.linspace(0, 1300, 1301)

        x1 = lt1.get_data('V(R1)', frequency=freq)
        x2 = lt2.get_data('V(R1)', frequency=freq)
        
        self.assertTrue(np.isclose(0, np.max(abs(x1) - abs(x2))))
        self.assertTrue(np.isclose(0, np.max(np.angle(x1) - np.angle(x2))))

    def test_reverse_x_dc_analysis(self):
        passed = True
        try:
            lt1 = Ltspice(path.join(self.__file_path, 'reverse_x_analysis.raw')).parse()
        except:
            passed = False
        
        self.assertTrue(passed)
        self.assertTrue(lt1.case_count == 28)


if __name__ == '__main__':
    unittest.main()

