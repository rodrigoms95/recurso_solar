import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

i = sys.argv[1]
internal = sys.argv[2]
files = [ f"zzR_zz_Mega0{i}_Variables_Extraidas.nc",
    f"WRF_miroc_1985_2014_{i}.nc" ]

with xr.open_dataset( f"{internal}/{files[0]}" ) as ds:

    ds["Wind_Speed"] = np.sqrt(ds["U10"]**2 + ds["V10"]**2).astype(np.float32)
    ds["T2"] = ds["T2"] - 273.15
    ds["XLAT"] = ds["XLAT"].isel({"west_east": 0})
    ds["XLONG"] = ds["XLONG"].isel({"south_north": 0})
    ds = ds.rename_vars( { "XLAT": "lat", "XLONG": "lon", "XTIME": "time",
        "T2": "Temperature", "SWDOWN": "GHI", "PSFC": "Pressure" } )
    ds = ds.swap_dims( { "south_north": "lat",
        "west_east": "lon", "XTIME": "time" } )
    ds = ds.drop_vars( ["U10", "V10", "Q2"] )

    ds.to_netcdf(f"{internal}/{files[1]}")