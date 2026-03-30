# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 15:36:47 2026

@author: FTNK-LocalAdm
"""

import pyvisa as visa
from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt
import time 
import struct
def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))


rm = visa.ResourceManager()
devs = rm.list_resources()
osc = rm.open_resource('GPIB1::10::INSTR')

# Set data output to WORD
osc.write(':WAVeform:FORMat WORD')
data = osc.query(':WAVeform:DATA?').split(',')

#%%

osc.write(":WAVeform:SOURce CHANnel1");
osc.write(":WAVeform:FORMat BYTE");
XINCrement = float(osc.query(":WAVeform:XINCrement?").strip());

XORigin = float(osc.query(":WAVeform:XORigin?").strip());
osc.query(":WAVeform:XREFerence?");

XREFerence = osc.query(":WAVeform:XREFerence?");
DATA = osc.query_binary_values(":WAVeform:DATA?");

YINCrement = float(osc.query(":WAVeform:YINCrement?").strip());
YORigin =  float(osc.query(":WAVeform:YORigin?").strip());

YREFerence =   float(osc.query(":WAVeform:YREFerence?").strip());
#%% ARRAY FORMATION

data_processed = []

for d in DATA:
    # Byte1 = int(binary(d)[:8], 2)
    # Byte2 = int(binary(d)[8:16], 2) 
    # Byte3 = int(binary(d)[16:24], 2) 
    # Byte4 = int(binary(d)[24:32], 2) 
    
    Byte1 = BitArray(bin=binary(d)[:8]).int
    Byte2 = BitArray(bin=binary(d)[8:16]).int
    Byte3 = BitArray(bin=binary(d)[16:24]).int
    Byte4 = BitArray(bin=binary(d)[24:32]).int

    
    data_processed.append(Byte1)
    data_processed.append(Byte2)
    data_processed.append(Byte3)
    data_processed.append(Byte4)

#%% Plotting properly

t_axis = np.arange(XORigin, XORigin + (len(data_processed)-0) * XINCrement, XINCrement)
plt.plot(t_axis, data_processed)



#%% Process

osc.write(":ACQuire:POINts 4096");

osc.query("WAVeform:POINts?")


osc.write(":TIMebase:POSition 26.8E-9");


 
#%% PROCEDURE

timeBase_1 = 28.8785;
osc.write(":TIMebase:POSition " + str(timeBase_1) + "E-9");
time.sleep(0.1)
DATA_1 = osc.query_binary_values(":WAVeform:DATA?");
time.sleep(0.1)
XORigin_1 = float(osc.query(":WAVeform:XORigin?").strip());
time.sleep(0.1)

timeBase_2 = timeBase_1 + 6.25
osc.write(":TIMebase:POSition " + str(timeBase_2) + "E-9");
time.sleep(0.1)
DATA_2 = osc.query_binary_values(":WAVeform:DATA?");
time.sleep(0.1)
XORigin_2 = float(osc.query(":WAVeform:XORigin?").strip());

data_processed_1 = []

for d in DATA_1:
    # Byte1 = int(binary(d)[:8], 2)
    # Byte2 = int(binary(d)[8:16], 2) 
    # Byte3 = int(binary(d)[16:24], 2) 
    # Byte4 = int(binary(d)[24:32], 2) 
    
    Byte1 = BitArray(bin=binary(d)[:8]).int
    Byte2 = BitArray(bin=binary(d)[8:16]).int
    Byte3 = BitArray(bin=binary(d)[16:24]).int
    Byte4 = BitArray(bin=binary(d)[24:32]).int

    
    data_processed_1.append(Byte1)
    data_processed_1.append(Byte2)
    data_processed_1.append(Byte3)
    data_processed_1.append(Byte4)
    
data_processed_2 = []

for d in DATA_2:
    # Byte1 = int(binary(d)[:8], 2)
    # Byte2 = int(binary(d)[8:16], 2) 
    # Byte3 = int(binary(d)[16:24], 2) 
    # Byte4 = int(binary(d)[24:32], 2) 
    
    Byte1 = BitArray(bin=binary(d)[:8]).int
    Byte2 = BitArray(bin=binary(d)[8:16]).int
    Byte3 = BitArray(bin=binary(d)[16:24]).int
    Byte4 = BitArray(bin=binary(d)[24:32]).int

    
    data_processed_2.append(Byte1)
    data_processed_2.append(Byte2)
    data_processed_2.append(Byte3)
    data_processed_2.append(Byte4)

plt.plot(t_axis, data_processed_2)
plt.plot(t_axis, data_processed_1)


import pandas as pd
import pickle

df_1 = pd.DataFrame(columns=['tVal','yVal'])
df_2 = pd.DataFrame(columns=['tVal','yVal'])

df_1['tVal'] = t_axis
df_1['yVal'] = data_processed_1

df_2['tVal'] = t_axis
df_2['yVal'] = data_processed_2

data_1 = {
    "df": df_1,
    "xOrigin": XORigin_1,
    "timeBase": timeBase_1
}

with open(r"C:\Users\FTNK-LocalAdm\OneDrive - Danmarks Tekniske Universitet\Jan Files\TimeDelay\BottomArm880mm\data_pulse_d0_bottom_880.pkl", "wb") as f:
    pickle.dump(data_1, f)
    
data_2 = {
    "df": df_2,
    "xOrigin": XORigin_2,
    "timeBase": timeBase_2
}

with open(r"C:\Users\FTNK-LocalAdm\OneDrive - Danmarks Tekniske Universitet\Jan Files\TimeDelay\BottomArm880mm\data_pulse_delayed_bottom_880.pkl", "wb") as f:
    pickle.dump(data_2, f)    
    
    
    

with open(r"C:\Users\FTNK-LocalAdm\OneDrive - Danmarks Tekniske Universitet\Jan Files\TimeDelay\BottomArm880mm\data_pulse_d0_bottom_880.pkl", "rb") as f:
    loaded = pickle.load(f)

df = loaded["df"]
var1 = loaded["xOrigin"]
var2 = loaded["timeBase"]


