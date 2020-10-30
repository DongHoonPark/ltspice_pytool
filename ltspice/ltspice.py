import os
from typing import List
import numpy as np
import re

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
        self._case_num  = 0   # case number
        self._variables = []  # variable list
        self._types     = []  # type list
        self._mode      = 'Transient' # support Transient, AC, FFT
        self._file_type = "" # Binary / Ascii
        self._precision = 'auto'

        self.header_size = 0
        self.read_header()

    def read_header(self):
        filesize = os.stat(self.file_path).st_size
        
        with open(self.file_path, 'rb') as f:
            if filesize > self.max_header_size:
                data = f.read(self.max_header_size)  
            else:
                data = f.read()  

        line = ''
        lines = []   
        fp_line_begin = 0
        fp_line_end = 0
        while not ('Binary' in line or 'Value' in line):
            if bytes([data[fp_line_end]]) == b'\n':
                line = str(bytes(data[fp_line_begin:fp_line_end+2]), encoding='UTF16')
                lines.append(line)
                fp_line_begin = fp_line_end+2
                fp_line_end   = fp_line_begin
            else:
                fp_line_end += 1
        lines = [x.rstrip() for x in lines]

        # remove string header from binary data 
        self.header_size = fp_line_end
        data = data[self.header_size:]

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
                self.offset = float(line[len(self.tags[5]):])

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
        else:
            raise UnknownFileTypeException
    
    def parse(self):
        if self._file_type == 'Binary':

            with open(self.file_path, 'rb') as f:
                data = f.read()[self.header_size:]

            if self._mode == 'FFT' or self._mode == 'AC':
                self.data_raw = np.frombuffer(data, dtype=np.complex128)
                self.time_raw = np.abs(self.data_raw[::self._variable_num])
                self.data_raw = np.reshape(self.data_raw, (self._point_num, self._variable_num))

            elif self._mode == 'Transient':
                #Check file length
                expected_data_len = self._point_num * (self._variable_num + 1) * 4

                if len(data) == expected_data_len:
                    self.data_raw = np.frombuffer(data, dtype=np.float32)
                    self.time_raw = np.zeros(self._point_num)

                    for i in range(self._point_num):
                        d = data[i * (self._variable_num + 1) * 4: i * (self._variable_num + 1) * 4 + 8]
                        self.time_raw[i] = np.frombuffer(d, dtype=np.float64)

                self.data_raw = np.reshape(np.array(self.data_raw), (self._point_num, self._variable_num + 1))

        elif self._file_type == 'Ascii':
            with open(self.file_path, 'r') as f:
                data = f.readlines()
              
        # Split cases
        self._case_num = 1
        self._case_split_point.append(0)

        start_value = self.time_raw[0]

        for i in range(self._point_num - 1):
            if self.time_raw[i] > self.time_raw[i + 1] and self.time_raw[i + 1] == start_value:
                self._case_num += 1
                self._case_split_point.append(i + 1)
        self._case_split_point.append(self._point_num)

    def getData(self, name, case=0, time=None):
        if ',' in name:
            variable_names = re.split(',|\(|\)', name)
            return self.getData('V(' + variable_names[1] + ')', case, time) - self.getData('V(' + variable_names[2] + ')', case, time)
        else:
            variables_lowered = [v.lower() for v in self._variables]

            if name.lower() not in variables_lowered:
                return None

            variable_index = variables_lowered.index(name.lower())

            if self._mode == 'Transient':
                variable_index += 1

            data = self.data_raw[self._case_split_point[case]:self._case_split_point[case + 1], variable_index]

            if time is None:
                return data
            else:
                return np.interp(time, self.getTime(case), data)

    def getTime(self, case=0):
        if self._mode == 'Transient':
            return np.abs(self.time_raw[self._case_split_point[case]:self._case_split_point[case + 1]])
        else:
            return None

    def getFrequency(self, case=0):
        if self._mode == 'FFT' or self._mode == 'AC':
            return np.abs(self.time_raw[self._case_split_point[case]:self._case_split_point[case + 1]])
        else:
            return None

    def getVariableNames(self, case=0):
        return self._variables

    def getVariableTypes(self, case=0):
        return self._types

    def getCaseNumber(self):
        return self._case_num

    def getVariableNumber(self):
        return len(self._variables)

    @property
    def time(self):
        return self.getTime(case=0)

    



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

