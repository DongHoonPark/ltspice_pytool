import os
from typing import List
import numpy as np
import re

from numpy.lib.utils import deprecate

class LtspiceException(Exception):
    pass
class VariableNotFoundException(LtspiceException):
    pass
class FileSizeNotMatchException(LtspiceException):
    pass
class UnknownFileTypeException(LtspiceException):
    pass


class Ltspice:
    max_header_size = int(100e3)
    def __init__(self, file_path):
        self.file_path = file_path
        self.dsamp = 1
        self.tags = ['Title:', 'Date:', 'Plotname:', 'Flags:', 'No. Variables:', 'No. Points:', 'Offset:']
        self.time_raw = []
        self.data_raw = []
        self._case_split_point = []

        #TODO : refactor header to another struct
        self.title = ''
        self.date = ''
        self.plot_name = ''
        self.flags = []
        self.offset = 0

        self._point_num = 0   # all point number
        self._variables = []  # variable list
        self._types     = []  # type list
        self._mode      = 'Transient' # support Transient, AC, FFT
        self._file_type = "" # Binary / Ascii
        self._variable_dtype = np.float32
        self._time_dtype     = np.float64
        self._encoding  = ''

        self.header_size = 0
        self.read_header()

    def set_variable_dtype(self, t):
        self._variable_dtype = t
        return self

    def read_header(self):
        filesize = os.stat(self.file_path).st_size
        
        with open(self.file_path, 'rb') as f:
            if filesize > self.max_header_size:
                data = f.read(self.max_header_size)  
            else:
                data = f.read()  

        #TODO : have to find adequate way to determine proper encoding of text..
        try:
            line = ''
            lines = []   
            fp_line_begin = 0
            fp_line_end = 0
            while not ('Binary' in line or 'Values' in line):
                if bytes([data[fp_line_end]]) == b'\n':
                    line = str(bytes(data[fp_line_begin:fp_line_end+2]), encoding='UTF16')
                    lines.append(line)
                    fp_line_begin = fp_line_end+2
                    fp_line_end   = fp_line_begin
                else:
                    fp_line_end += 1
            self._encoding = 'utf-16-le'
        except UnicodeDecodeError as e:
            line = ''
            lines = []   
            fp_line_begin = 0
            fp_line_end = 0
            while not ('Binary' in line or 'Values' in line):
                if bytes([data[fp_line_end]]) == b'\n':
                    line = str(bytes(data[fp_line_begin:fp_line_end+1]), encoding='UTF8')
                    lines.append(line)
                    fp_line_begin = fp_line_end+1
                    fp_line_end   = fp_line_begin
                else:
                    fp_line_end += 1
            self._encoding = 'utf-8'


        lines = [x.rstrip().rstrip() for x in lines]

        # remove string header from binary data 
        self.header_size = fp_line_end

        vindex = lines.index('Variables:')
        header_text   = lines[0:vindex]
        variable_text = lines[vindex+1:-1]

        for line in header_text:
            if self.tags[0] in line:
                self.title = line[len(self.tags[0]):]
            if self.tags[1] in line:
                self.date = line[len(self.tags[1]):]
            if self.tags[2] in line:
                self.plot_name = line[len(self.tags[2]):]
            if self.tags[3] in line:
                self.flags = line[len(self.tags[3]):].split(' ')
            if self.tags[4] in line:
                self._variable_num = int(line[len(self.tags[4]):])
            if self.tags[5] in line:
                self._point_num = int(line[len(self.tags[5]):])
            if self.tags[6] in line:
                self.offset = float(line[len(self.tags[6]):])

        for elem in variable_text:
            vdata = elem.split()
            self._variables.append(vdata[1])
            self._types.append(vdata[2])

        # check mode
        if 'FFT' in self.plot_name:
            self._mode = 'FFT'
        elif 'Transient' in self.plot_name:
            self._mode = 'Transient'
        elif 'AC' in self.plot_name:
            self._mode = 'AC'

        # check file type
        if 'Binary' in lines[-1]:
            self._file_type = 'Binary'
        elif 'Value' in lines[-1]:
            self._file_type = 'Ascii'
            self._variable_dtype = np.float64
        else:
            raise UnknownFileTypeException

        if self._mode == 'FFT' or self._mode == 'AC':
            self._variable_dtype = np.complex128
            self._time_dtype = np.complex128
        pass
    
    def parse(self):
        if self._file_type == 'Binary':
            #Check data size
            variable_data_size = np.dtype(self._variable_dtype).itemsize  
            time_data_size     = np.dtype(self._time_dtype).itemsize  
            diff = int(( time_data_size - variable_data_size ) / variable_data_size)

            variable_data_len  = self._point_num * (self._variable_num - 1) * variable_data_size
            time_data_len      = self._point_num * time_data_size
            expected_data_len  = variable_data_len + time_data_len

            with open(self.file_path, 'rb') as f:
                data = f.read()[self.header_size:]
            
            if not len(data) == expected_data_len:
                raise FileSizeNotMatchException

            if self._variable_dtype == self._time_dtype:
                _dtype = self._time_dtype
                self.data_raw = np.frombuffer(data, dtype=_dtype)
                self.time_raw = self.data_raw[::self._variable_num]
                self.data_raw = np.reshape(self.data_raw, (self._point_num, self._variable_num))
            else:
                self.data_raw = np.frombuffer(data, dtype=self._variable_dtype)
                self.time_raw = np.zeros(self._point_num, dtype=self._time_dtype)
                for i in range(self._point_num):
                    d = data[
                            i * (self._variable_num + diff) * variable_data_size:
                            i * (self._variable_num + diff) * variable_data_size + time_data_size
                        ]
                    self.time_raw[i] = np.frombuffer(d, dtype=self._time_dtype)

                self.data_raw = np.reshape(np.array(self.data_raw), (self._point_num, self._variable_num + diff))
                self.data_raw = self.data_raw[:, diff:]
                self.data_raw[:,0] = self.time_raw
                
        elif self._file_type == 'Ascii':
            with open(self.file_path, 'r', encoding=self._encoding) as f:
                data = f.readlines()
            data = [x.rstrip() for x in data]
            data = data[data.index('Values:') + 1:]
            _dtype = self._variable_dtype
            if _dtype == np.float64 or _dtype == np.float32:
                self.data_raw = np.array([self._variable_dtype(
                    x.split('\t')[-1]
                    ) for  x  in data]).reshape((self._point_num, self._variable_num))
                pass
            if _dtype == np.complex128 or _dtype == np.complex64:
                self.data_raw = np.array([self._variable_dtype(
                    complex(*[float(y) for y in x.split('\t')[-1].split(',')])
                    ) for  x  in data]).reshape((self._point_num, self._variable_num))
                pass
            self.time_raw = self.data_raw[:,0]
            pass
              
        # Split cases
        self._case_split_point.append(0)

        start_value = self.time_raw[0]

        for i in range(self._point_num - 1):
            if self.time_raw[i] > self.time_raw[i + 1] and self.time_raw[i + 1] == start_value:
                self._case_split_point.append(i + 1)
        self._case_split_point.append(self._point_num)
        return self

    def get_data(self, name, case=0, time=None, frequency=None):
        if ',' in name:
            variable_names = re.split(r',|\(|\)', name)
            return self.getData('V(' + variable_names[1] + ')', case, time) - self.getData('V(' + variable_names[2] + ')', case, time)
        else:
            variables_lowered = [v.lower() for v in self._variables]

            if name.lower() not in variables_lowered:
                return None

            variable_index = variables_lowered.index(name.lower())

            data = self.data_raw[self._case_split_point[case]:self._case_split_point[case + 1], variable_index]

            if time is None and frequency is None:
                return data
            elif not time is None:
                return np.interp(time, self.get_time(case), data)
            elif not frequency is None:
                return np.interp(frequency, self.get_frequency(case), data)
            else:
                return None 
    
    def get_time(self, case=0):
        if self._mode == 'Transient':
            return np.abs(self.time_raw[self._case_split_point[case]:self._case_split_point[case + 1]])
        else:
            return None

    def get_frequency(self, case=0):
        if self._mode == 'FFT' or self._mode == 'AC':
            return np.abs(self.time_raw[self._case_split_point[case]:self._case_split_point[case + 1]])
        else:
            return None
    
    @property
    def variables(self):
        return self._variables

    @property
    def time(self):
        return self.getTime(case=0)

    @property
    def frequency(self):
        return self.get_frequency(case=0)

    @property
    def case_count(self):
        return len(self._case_split_point) - 1

    @deprecate
    def getData(self, name, case=0, time=None):
        return self.get_data(name, case, time)

    @deprecate
    def getTime(self,case=0):
        return self.get_time(case)

    @deprecate
    def getFrequency(self, case=0):
        return self.get_frequency(case)

    @deprecate
    def getVariableNames(self, case=0):
        return self._variables

    @deprecate
    def getVariableTypes(self, case=0):
        return self._types

    @deprecate
    def getCaseNumber(self):
        return len(self._case_split_point)

    @deprecate
    def getVariableNumber(self):
        return len(self._variables)


    



def integrate(time, var, interval=None):
    # Valid interval check 
    if isinstance(interval, list):
        if len(interval) == 2:
            if max(time) < max(interval):
                return 0
            else:
                pass
        else:
            return 0
    elif interval is None:
        # If interval is None, integrate full range of time
        interval = [0, max(time)]
    else:
        return 0

    # Find begin/ end time index
    begin = np.searchsorted(time, interval[0])
    end   = np.searchsorted(time, interval[1])
    if len(time)-1 < end:
        end = len(time) - 1  # Overflow guard
    
    # Integrate it and return result
    result = np.trapz(var[begin:end], x=time[begin:end])

    return result

