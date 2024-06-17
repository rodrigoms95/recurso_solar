import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

import xesmf as xe

i = sys.argv[1]
n = sys.argv[2]
internal_data = sys.argv[3]
internal = sys.argv[4]
dataset = sys.argv[5]
files = [ f"{internal_data}/years/{dataset}_{i}.nc",
    f"{internal_data}/NSRDB_{n}km_0.nc",
    f"{internal}/{dataset}_{n}km_weights.nc",
    f"{internal}/years/{dataset}_{n}km_{i}.nc" ]

ds = []
for f in files[:-1]: ds.append( xr.open_dataset( f ) )

ds[0] = ds[0].isel({"lat": slice(5, -5), "lon": slice(5, -5)})
if n == 4: ds[1] = ds[1].isel({"lat": slice(4, -5), "lon": slice(4,  -5)})
else     : ds[1] = ds[1].isel({"lat": slice(9, -9), "lon": slice(8, -10)}) 

regridder = xe.Regridder( ds[0], ds[1],
    method = "bilinear", weights = ds[2] )
regridder( ds[0] ).to_netcdf(files[-1])