import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

import xesmf as xe


i = int(sys.argv[1])
path_d = "temp/WRF_miroc_1985_2014_2km/year/"
files = sorted(os.listdir(path_d))
if ".DS_Store" in files: files.remove(".DS_Store")

ds_i = []

lat_i = [0, 0, 0, 42, 42, 42, 84, 84, 84]
lat_f = [42, 42, 42, 84, 84, 84, 126, 126, 126]
lon_i = [0, 53, 106, 0, 53, 106, 0, 53, 106]
lon_f = [53, 106, 158, 53, 106, 158, 53, 106, 158]

for f in files:
    ds_i.append( xr.open_dataset( path_d + f ).isel(
        {"lat": slice(lat_i[i], lat_f[i]),
         "lon": slice(lon_i[i], lon_f[i])} ) )

ds = xr.concat(ds_i, dim = "time").to_netcdf(
    f"temp/grid/WRF_miroc_1985_2014_2km_{i}.nc" )