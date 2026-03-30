"""
Functions to control the laser
"""
#%%
import serial
import time
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import pyvisa as visa
import tqdm
from ThorlabsPM100 import ThorlabsPM100

class ThorlabsPowermeter:
    
    def __init__(self, address, wavelength=1550):
        rm = visa.ResourceManager()
        #devs = rm.list_resources()
        powerMeter = rm.open_resource(address)
        powerMeter.write('CONF:POW')
        
        self.pm = ThorlabsPM100(inst=powerMeter)
        self.set_correction_wavelength(wavelength)
        
    def set_correction_wavelength(self, wavelength):
        self.pm.sense.correction.wavelength = wavelength
        
    def read(self):
        return self.pm.read
    

class CobriteLaser:

    def __init__(self, COM:int, baudrate=115200):
        self.com_port = "COM" + str(COM)
        self.baudrate = baudrate
        self.ser = None
        self.sep = ";" 

        self.power_dbm = None
        self.wavelength_nm = None 

    def connect(self):
        try:
            self.ser = serial.Serial(self.com_port, self.baudrate, timeout=2)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"Connected to COM {self.com_port}")
            self.query("pass IDP")
            idn = self.query("*idn?")
            print(f"Device ID: {idn}")
        except Exception as e:
            print(f"Connection Error: {e}")

    def query(self, command):
        if not self.ser: return
        full_cmd = f"{command}{self.sep}"
        self.ser.write(full_cmd.encode('utf-8'))
        reply = ""
        start_time = time.time()
        while self.sep not in reply:
            if (time.time() - start_time) > 5: 
                break
            if self.ser.in_waiting > 0:
                reply += self.ser.read(self.ser.in_waiting).decode('utf-8')
        clean_reply = reply.replace(self.sep, "").strip()
        #print(f"TX: {command} -> RX: {clean_reply}")
        return clean_reply

    def set_wavelength(self, wavelength_nm, card=1, port=1):
        self.wavelength_nm = wavelength_nm
        self.query(f"wav {card},1,{port},{wavelength_nm}")

        # print("Tuning... please wait.", end='\r')
        # self.query(f"bwai {card},1,{port}")
        # print("Laser is stable and ON.          ")

    def set_power(self, power_dbm, card=1, port=1):
        self.power_dbm = power_dbm
        self.query(f"pow {card},1,{port},{power_dbm}")

        # print("Tuning... please wait.", end='\r')
        # self.query(f"bwai {card},1,{port}")
        # print("Laser is stable and ON.          ")

    def turn_on(self, card=1, port=1):
        self.query(f"stat {card},1,{port},1")

    def turn_off(self, card=1, port=1):
        self.query(f"stat {card},1,{port},0")

    def close(self):
        if self.ser:
            self.ser.close()
            print("Connection closed.")

#%%
rm = visa.ResourceManager()
devs = rm.list_resources()
print(devs)
#%%
# Laser
laser = CobriteLaser(COM=11)
laser.connect()
laser.set_power(6)  # Set power to 10 dBm
laser.turn_on()

#%%
# Powermeter
pm = ThorlabsPowermeter(address='USB0::0x1313::0x8078::P0024464::0::INSTR', 
                        wavelength=1550)

pm_2 = ThorlabsPowermeter(address='USB0::0x1313::0x8078::P0051186::0::INSTR', 
                        wavelength=1550)

#%%
wavelengths = np.arange(1530, 1565, 0.1)  # Wavelengths from 1540 nm to 1560 nm in steps of 0.5 nm
powers_dbm = []
powers_dbm_2 = []

for wl in tqdm.tqdm(wavelengths):
    laser.set_wavelength(wl)
    pm.set_correction_wavelength(wl)
    pm_2.set_correction_wavelength(wl)
    time.sleep(15)
  # Wait for the laser to stabilize at the new wavelength
    power = pm.read()
    power_2 = pm_2.read()
    powers_dbm.append(10 * np.log10(power * 1e3))  # Convert Watts to dBm
    powers_dbm_2.append(10 * np.log10(power_2 * 1e3))
    #print(f"Set wavelength to {wl} nm, measured power: {powers_dbm[-1]:.2f} dBm")


#%%
# Convert Watts to dBm
plt.figure(figsize=(8,5))
plt.plot(wavelengths, powers_dbm, marker='o')
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
plt.title('AMZI-1 Wavelength Sweep using Cobrite Laser and Thorlabs Powermeter 1')
plt.xlabel('Wavelength [nm]')
plt.ylabel('Power [dBm]')
plt.savefig(os.path.join(downloads_folder, 'Wavelength_sweep_Cobrite_AMZI_1.png'), dpi=300)

#%%
# Convert Watts to dBm
plt.figure(figsize=(8,5))
plt.plot(wavelengths, powers_dbm_2, marker='o')
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
plt.title('Coupler 5-6 Wavelength Sweep using Cobrite Laser and Thorlabs Powermeter 2')
plt.xlabel('Wavelength [nm]')
plt.ylabel('Power [dBm]')
plt.savefig(os.path.join(downloads_folder, 'Wavelength_sweep_Cobrite_2.png'), dpi=300)

# Save data to CSV
data = pd.DataFrame({'Wavelength (nm)': wavelengths, 'Power (dBm)': powers_dbm})
data_2 = pd.DataFrame({'Wavelength (nm)': wavelengths, 'Power (dBm) - PM2': powers_dbm_2})
data.to_csv(os.path.join(downloads_folder, 'Wavelength_sweep_Cobrite_PM1_AMZI_1.csv'), index=False)
data_2.to_csv(os.path.join(downloads_folder, 'Wavelength_sweep_Cobrite_PM2_coupler_5_6.csv'), index=False)


#%%
laser.turn_off()
laser.close()
# %%
