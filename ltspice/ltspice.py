import os
import struct
import numpy as np
import itertools
import re


class Ltspice:
    file_path = ''
    dsamp = 1
    tags = ['Title:', 'Date:', 'Plotname:', 'Flags:', 'No. Variables:', 'No. Points:']
    time_raw = []
    data_raw = []
    _case_split_point = []

    title = ''
    date = ''
    plot_name = ''
    flags = ''

    _point_num = 0   # all point number
    _case_num  = 0   # case number
    _variables = []  # variable list
    _types     = []  # type list
    _mode      = 'Transient'

    def __init__(self, file_path):
        self.file_path = file_path
    
    def parse(self, dsamp=1):
        self.dsamp = dsamp
        size = os.path.getsize(self.file_path)
        tmp = b''
        lines = []
        line = ''

        with open(self.file_path, 'rb') as f:
            data = f.read()  # Binary data read
            f.close()

        bin_index = 0

        while 'Binary' not in line:
            tmp = tmp + bytes([data[bin_index]])
            if bytes([data[bin_index]]) == b'\n':
                bin_index = bin_index+1
                tmp = tmp + bytes([data[bin_index]])
                line = str(tmp, encoding='UTF16')
                lines.append(line)
                tmp = b''
            bin_index = bin_index+1

        vindex = 0
        for index, line in enumerate(lines):
            if self.tags[0] in line:
                self.title = line[len(self.tags[0]):]
            if self.tags[1] in line:
                self.date = line[len(self.tags[1]):]
            if self.tags[2] in line:
                self.plot_name = line[len(self.tags[2]):]
            if self.tags[3] in line:
                self.flags = line[len(self.tags[3]):]
            if self.tags[4] in line:
                self._variable_num = int(line[len(self.tags[4]):])
            if self.tags[5] in line:
                self._point_num = int(line[len(self.tags[5]):])
            if 'Variables:' in line:
                vindex = index

        for j in range(self._variable_num):
            vdata = lines[vindex + j + 1].split()
            self._variables.append(vdata[1])
            self._types.append(vdata[2])

        if 'FFT' in self.plot_name:
            self._mode = 'FFT'
        elif 'Transient' in self.plot_name:
            self._mode = 'Transient'
        elif 'AC' in self.plot_name:
            self._mode = 'AC'


        if self._mode == 'FFT' or self._mode == 'AC':
            self.data_raw = np.frombuffer(data[bin_index:], dtype=np.complex128)
            self.time_raw = np.abs(self.data_raw[::self._variable_num])
            self.data_raw = np.reshape(self.data_raw, (self._point_num, self._variable_num))

        elif self._mode == 'Transient':
            #Check file length
            expected_data_len = self._point_num * (self._variable_num + 1) * 4

            if len(data) - bin_index == expected_data_len:
                self.data_raw = np.frombuffer(data[bin_index:], dtype=np.float32)
                self.time_raw = np.zeros(self._point_num)
                for i in range(self._point_num):
                    d = data[bin_index + i * (self._variable_num + 1) * 4: bin_index + i * (self._variable_num + 1) * 4 + 8]
                    self.time_raw[i] = struct.unpack('d', d)[0]

            self.data_raw = np.reshape(np.array(self.data_raw), (self._point_num, self._variable_num + 1))

        # Split cases
        self._case_num = 1
        self._case_split_point.append(0)

        start_value = self.time_raw[0]

        for i in range(self._point_num - 1):
            if self.time_raw[i] > self.time_raw[i + 1] and self.time_raw[i + 1] == start_value:
                self._case_num += 1
                self._case_split_point.append(i + 1)
        self._case_split_point.append(self._point_num)

    def getData(self, variable, case=0, time=None):
        if ',' in variable:
            variable_names = re.split(',|\(|\)', variable)
            return self.getData('V(' + variable_names[1] + ')', case, time) - self.getData('V(' + variable_names[2] + ')', case, time)
        else:
            variables_lowered = [v.lower() for v in self._variables]

            if variable.lower() not in variables_lowered:
                return None

            variable_index = variables_lowered.index(variable.lower())

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

