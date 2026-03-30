#%%
"""
sweep_santec_pm320e.py
Created on 2026-02-26
Author: Jan Scarabelli Calopa

New version of Lab_Codes/wavelength_sweep_santec.py to use 
with PM320E instead of PM100 
"""
from Functions import *
import tqdm
import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print(resources)  # Should list something like 'USB0::1313::8022::SN::INSTR'

inst = rm.open_resource(resources[0])
print(inst.query("*IDN?"))


#%%
# Laser
laser = SantecLaser(GPIB=28, timeout=10000)
laser.connect()
laser.turn_on()
laser.set_power(6)
laser.set_wavelength(1550)

 #%%
# Powermeter
pm = ThorlabsPM100('USB0::0x1313::0x8078::P0017921::INSTR') 
                        # wavelength=1550)

pm2 = ThorlabsPM100('USB0::0x1313::0x8078::P0024464::INSTR') 
                        # wavelength=1550)



#%%

powers_dbm = []
powers_dbm_2 = []

wavelengths = np.arange(1530, 1565, 0.1)
laser.set_wavelength(wavelengths[0])
time.sleep(5)
for wl in tqdm.tqdm(wavelengths):
    new_wl = round(float(wl),2)
    laser.set_wavelength(new_wl)
    pm.set_correction_wavelength(new_wl) 
    pm2.set_correction_wavelength(new_wl)
    time.sleep(1)
  # Wait for the laser to stabilize at the new wavelength
    power = pm.read()
    power2 = pm2.read()
    powers_dbm.append(10 * np.log10(power * 1e3)) 
    powers_dbm_2.append(10 * np.log10(power2 * 1e3))
    #print(f"Set wavelength to {wl} nm, measured power: {powers_dbm[-1]:.2f} dBm   ", end='\r')

#%%
# Convert Watts to dBm
plt.figure(figsize=(8,5))
plt.plot(wavelengths, powers_dbm, marker='o')
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
plt.title('AMZI-1 Wavelength Sweep using Cobrite Laser and Thorlabs Powermeter')
plt.xlabel('Wavelength [nm]')
plt.ylabel('Power [dBm]')
plt.savefig(os.path.join(downloads_folder, 'Wavelength_sweep_Santec_AMZI_1.png'), dpi=300)

plt.figure(figsize=(8,5))
plt.plot(wavelengths, powers_dbm_2, marker='o')
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
plt.title('Couplers 5-6 Wavelength Sweep using Cobrite Laser and Thorlabs Powermeter')
plt.xlabel('Wavelength [nm]')
plt.ylabel('Power [dBm]')
plt.savefig(os.path.join(downloads_folder, 'Wavelength_sweep_Santec_couplers_5_6.png'), dpi=300)

np.savetxt(
    os.path.join(downloads_folder, 'Wavelength_sweep_Santec.txt'),
    np.column_stack((wavelengths, powers_dbm, powers_dbm_2))
)
#%%
# laser = SantecLaser(GPIB=28, timeout=10000)
# laser.connect()
laser.turn_off()
laser.close()

#%%
from Functions import *