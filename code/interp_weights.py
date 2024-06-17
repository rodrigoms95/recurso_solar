import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

import xesmf as xe

n = sys.argv[1]
internal_data = sys.argv[2]
internal = sys.argv[3]
dataset = sys.argv[4]

files = [ f"{internal_data}/years/{dataset}_0.nc",
    f"{internal_data}/NSRDB_{n}km_0.nc" ]
path_r = f"{internal}/{dataset}_{n}km_weights.nc"

ds = []
for f in files: ds.append( xr.open_dataset( f ) )

ds[0] = ds[0].isel({"lat": slice(5, -5), "lon": slice(5, -5)})
if n == 4: ds[1] = ds[1].isel({"lat": slice(4, -5), "lon": slice(4,  -5)})
else     : ds[1] = ds[1].isel({"lat": slice(9, -9), "lon": slice(8, -10)}) 

xe.Regridder( ds[0], ds[1], method = "bilinear" ).to_netcdf(path_r)