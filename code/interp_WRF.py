import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

import xesmf as xe

i = sys.argv[1]
path_d = "temp/WRF_miroc_1985_2014/"
files = [ f"WRF_miroc_1985_2014_{i}.nc", "NSRDB_2km.nc",
    "WRF_miroc_1985_2014_2km_weights.nc", f"WRF_miroc_1985_2014_2km_{i}.nc" ]
path_r = f"temp/WRF_miroc_1985_2014_2km/"

ds = []
for f in files[:-1]: ds.append( xr.open_dataset(path_d + f ) )

ds[1] = ds[1].isel({"lat": slice(3, -4), "lon": slice(1, -3)})
regridder = xe.Regridder( ds[0], ds[1],
    method = "bilinear", weights = ds[2] )
regridder( ds[0] ).to_netcdf(path_r + files[-1])