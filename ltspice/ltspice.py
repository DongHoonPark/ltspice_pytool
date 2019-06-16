import os
import struct
import numpy as np
import itertools
import re
 
class Ltspice:
    filepath = ''
    dsamp = 1
    tags = ['Title:', 'Date:', 'Plotname:', 'Flags:', 'No. Variables:', 'No. Points:' ]
    time_raw = []
    data_raw = []
    time_split_point = []

    title=''
    date=''
    plotname=''
    flags=''

    v_number = 0 # variable number
    p_number = 0 # all point number
    c_number = 0 # case number

    v_list = [] # variable list
    t_list = [] # type list

    def __init__(self, filepath):
        self.filepath = filepath
        self.time_raw = []
        self.data_raw = []
        self.time_split_point = []
        self.v_list = []
        self.t_list = []
    
    def parse(self, dsamp=1):
        self.__init__(self.filepath)
        self.dsamp = dsamp
        size = os.path.getsize(self.filepath)
        fo = open(self.filepath,'rb')
        tmp = b''
        lines = []
        line = ''
        data = fo.read() # Binary data read
        fo.close()
        i=0

        while 'Binary' not in line:
            tmp = tmp + bytes([data[i]])
            if(bytes([data[i]]) == b'\n'):
                i = i+1
                tmp = tmp + bytes([data[i]])
                line = str(tmp, encoding='UTF16')
                lines.append(line)
                tmp = b''
            i = i+1

        vindex = 0
        for index,l in enumerate(lines):
            if(self.tags[0] in l):
                self.title = l[len(self.tags[0]):]
            if(self.tags[1] in l):
                self.date = l[len(self.tags[1]):]
            if(self.tags[2] in l):
                self.plotname = l[len(self.tags[2]):]
            if(self.tags[3] in l):
                self.flags = l[len(self.tags[3]):]
            if(self.tags[4] in l):
                self.v_number = int(l[len(self.tags[4]):])
            if(self.tags[5] in l):
                self.p_number = int(l[len(self.tags[5]):])
            if('Variables:' in l):
                vindex = index

        for j in range(self.v_number):
            vdata = lines[vindex+j+1].split()
            self.v_list.append(vdata[1])
            self.t_list.append(vdata[2])

        self.data_raw = struct.unpack(str(self.p_number*(self.v_number+1))+'f', data[i:size])

        self.time_raw = [None]*self.p_number
        for i in range(self.p_number):
            self.time_raw[i] = struct.unpack('d', struct.pack('f',self.data_raw[i*(self.v_number+1)]) + struct.pack('f',self.data_raw[1+i*(self.v_number+1)]))[0]
        
        self.time_raw = np.array(self.time_raw)

        self.c_number = 1
        self.time_split_point.append(0)
        for i in range(self.p_number-1):
            if(self.time_raw[i] > self.time_raw[i+1] and self.time_raw[i+1]==0):
                self.c_number = self.c_number+1
                self.time_split_point.append(i+1) 
        self.time_split_point.append(self.p_number)

        self.data_raw = np.reshape(np.array(self.data_raw), (self.p_number, (self.v_number+1)))
    
    def getData(self, v_name, case=0, time=None):
        if(',' in v_name):
            v_names = re.split(',|\(|\)',v_name)
            return self.getData('V('+v_names[1]+')', case, time) - self.getData('V('+v_names[2]+')', case, time)
        else:
            v_num = 0
            for index,vl in enumerate(self.v_list):
                if(v_name.lower()== vl.lower()):
                    v_num = index+1
            if(v_num == 0):
                return None
            else:
                data = self.data_raw[self.time_split_point[case]:self.time_split_point[case+1], v_num]
                if(time == None):
                    return data
                else:
                    return np.interp(time, self.getTime(case), data)
                    
                

    def getTime(self, case=0):
        return np.abs(self.time_raw[self.time_split_point[case]:self.time_split_point[case+1]])

    def getVariableNames(self, case=0):
        return self.v_list

    def getVariableTypes(self, case=0):
        return self.t_list

    def getCaseNumber(self):
        return self.c_number

    def getVariableNumber(self):
        return self.v_number

def integrate(time, var, interval=None):
    # Valid interval check 
    if(type(interval)==list):
        if(len(interval) == 2):
            if(max(time) < max(interval)):
                return 0
            else:
                pass
        else:
            return 0
    elif(interval == None):
        #If interval is None, integrate full range of time
        interval = [0, max(time)]
    else:
        return 0

    #Find begin/ end time index
    begin = np.searchsorted(time, interval[0])
    end   = np.searchsorted(time, interval[1])
    if(len(time)-1 < end):
        end = len(time) - 1 #Overflow guard
    
    #Integrate it and return result
    result = np.trapz(var[begin:end], x=time[begin:end])
    return result

    

class Tools:
    def __init__(self):
        self.metaParam = 'MParameter'
        self.paramTableLines = []

    def genParamTable(self, param_names, param_case):
        metaParamDeclareLine = '.step param '+self.metaParam+' list '
        case = 1
        
        for i in range(param_names.__len__()):
            case = case * param_case[i].__len__()
            self.paramTableLines.append('.param '+param_names[i]+' = table('+self.metaParam)

        caselist = list(itertools.product(*param_case))

        for i in range(case):
            metaParamDeclareLine = metaParamDeclareLine + ' ' + str(i) 
            for j in range(param_names.__len__()):
                self.paramTableLines[j] = self.paramTableLines[j] + ',' + str(i) + ',' + str(caselist[i][j])

        print(metaParamDeclareLine)
        for i in range(param_names.__len__()):
            self.paramTableLines[i] = self.paramTableLines[i] + ')'
            print(self.paramTableLines[i])
