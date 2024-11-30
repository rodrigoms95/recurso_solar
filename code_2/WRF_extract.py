# Extrae variables de WRF

import os
import sys
import numpy as np
import xarray as xr

# Cargamos datos.
scn   = sys.argv[1]
#dir_o = "/home/rodr/buffalo/rodr/WRF/"
dir_o = "/datos/rodr/Datos/WRF_data/"
dir_d = f"{dir_o}{scn}/{scn}/"
dir_r = f"{dir_o}{scn}/data/"
if not os.path.exists(dir_r): os.mkdir(dir_r)
files = os.listdir(dir_d)
files.sort

print("Extrayendo variables")
for f in files:
    print(f"{f}               ", end = "\r")
    if scn=="NSRDB":
        if not os.path.exists(dir_r + f):
            ds = xr.open_dataset(dir_d + f).rename_vars(
                {"Wind Speed": "Wind_speed"})[
                ["GHI", "Temperature", "Wind_speed"]
                ].shift({"time": 7}).astype(np.float32)
            ds.to_netcdf(dir_r + f)
    else:
        if not os.path.exists(dir_r + "_".join(f.split("_")[1:])):
            ds = xr.open_dataset(dir_d + f)[["T2", "U10", "V10", "SWDOWN"]]
            # Temperatura
            ds["Temperature"] = (ds["T2"] - 273.15).astype(np.float32)
            # Velocidad del viento
            ds["Wind_speed"] = np.sqrt(ds["U10"]**2
                + ds["V10"]**2).astype(np.float32)
            # Radiación solar
            ds = ds.rename_vars({"SWDOWN": "GHI"})
            ds["GHI"] = ds["GHI"].astype(np.float32)
            # Guardamos el nuevo archivo
            ds = ds.drop_vars(["T2", "U10", "V10"])
            ds.to_netcdf(dir_r + f[16:])
print()
print()