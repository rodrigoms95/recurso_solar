import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

import xesmf as xe

i = sys.argv[1]
n = sys.argv[2]
internal = sys.argv[3]
dataset = sys.argv[4]
path_d = f"{internal}/"
files = [ f"years/{dataset}_{i}.nc", f"NSRDB_{n}km_0.nc",
    f"{dataset}_{n}km_weights.nc",
    f"years/{dataset}_{n}km_{i}.nc" ]
path_r = f"{internal}/{dataset}_{n}km/"

ds = []
for f in files[:-1]: ds.append( xr.open_dataset(path_d + f ) )

ds[0] = ds[0].isel({"lat": slice(5, -5), "lon": slice(5, -5)})
if n == 4: ds[1] = ds[1].isel({"lat": slice(4, -5), "lon": slice(4,  -5)})
else     : ds[1] = ds[1].isel({"lat": slice(9, -9), "lon": slice(8, -10)}) 

regridder = xe.Regridder( ds[0], ds[1],
    method = "bilinear", weights = ds[2] )
regridder( ds[0] ).to_netcdf(path_r + files[-1])