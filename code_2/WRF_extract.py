# Extrae variables de WRF

import os
import numpy as np
import xarray as xr

# Cargamos datos.
dir_d = "/home/rodr/buffalo/rodr/WRF/2040_2060/"
dir_r = "/home/rodr/buffalo/rodr/WRF/2040_2060_data/"
files = os.listdir(dir_d)
files.sort
for f in files:
    print(f)
    ds = xr.open_dataset(dir_d + f)[["T2", "U10", "V10", "SWDOWN"]]
    # Temperatura
    ds["Temperature"] = (ds["T2"] - 273.15).astype(np.float32)
    # Velocidad del viento
    ds["Wind_speed"] = np.sqrt(ds["U10"]**2 + ds["V10"]**2).astype(np.float32)
    # Radiación solar
    ds = ds.rename_vars({"SWDOWN": "GHI"})
    ds["GHI"] = ds["GHI"].astype(np.float32)
    # Guardamos el nuevo archivo
    ds = ds.drop_vars(["T2", "U10", "V10"])
    ds.to_netcdf(dir_r + f[16:])