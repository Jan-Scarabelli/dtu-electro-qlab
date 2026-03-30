"""
Created on 2026-02-24

Project: OneDrive-DanmarksTekniskeUniversitet
Author: Jan Scarabelli Calopa
"""

#%% Imports
import qontrol
import time

import pandas as pd

#%% Stablish connection with drivers
q = qontrol.QXOutput(serial_port_name="COM9")


#%% Define heater DAC to apply voltage to 
heater = 10

#%% Apply voltage to heater
voltage = 2.0
q.v[heater] = voltage

#%% Check
print(f"Applied voltage: {q.v[heater]} V")


#%% Test heater

n_vals = 100
time_interval = 0.5
voltage = 2.0

heaters = [i for i in range(9,18)]
for h in heaters:
    q.v[h] = voltage


#%%
rows = []

for i in range(100):  # 100 points per heater
    for h in heaters:
        rows.append({
            "Sample": i,          # keeps the time/sample index
            "Heater": h,
            "Voltage": q.v[h],
            "Current": q.i[h],
        })
    time.sleep(time_interval)
    print(f"\rIteration: {i}/{n_vals}", end="", flush=True)

data = pd.DataFrame(rows)

#%%
jan_onedrive_folder = "C:\\Users\\FTNK-LocalAdm\\OneDrive - Danmarks Tekniske Universitet (1)\\Jan Files\\voltage_check_pads"
file_path = jan_onedrive_folder + "\\voltage_heaters_conA.csv"
data.to_csv(f"{file_path}", index=True)

#%% Turn off
for h in heaters:
    q.v[h] = 0


#%% Loop for testing
while True:
    print(f"\rVoltage: {q.v[heater]:.4f}, Current: {q.i[heater]:.4f}", end="", flush=True)
    time.sleep(0.2)
