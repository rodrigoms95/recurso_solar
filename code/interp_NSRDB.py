import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

import xesmf as xe

year = sys.argv[1]
internal = sys.argv[2]

path_d = f"{internal}/NSRDB_2km_interp/"
path_w = f"{internal}/WRF_miroc_1985_2014/NSRDB_weights.nc"
path_r = f"{internal}/NSRDB_2km_interp/years/NSRDB_2km_interp_{year}.nc"
names = [ f"NSRDB_4km_{year}.nc", "NSRDB_2km_0.nc" ]
ds_4 = xr.open_dataset(path_d + names[0]).isel(
    {"lat": slice(4, -5), "lon": slice(4,  -5)})
ds_2 = xr.open_dataset(path_d + names[1]).isel(
    {"lat": slice(10, -11), "lon": slice(9, -10)}) 

# Cambiamos la resolución.
xe.Regridder( ds_4, ds_2, method = "bilinear" ).to_netcdf(path_w)

ds_w = xr.open_dataset(path_w)
regridder = xe.Regridder( ds_4, ds_2, method = "bilinear", weights = ds_w )
regridder( ds_4 ).to_netcdf(path_r)