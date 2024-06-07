import os
import sys

import xarray as xr

import xesmf as xe


i = int(sys.argv[1])
n = int(sys.argv[2])
path_d = f"temp/WRF_miroc_1985_2014_{n}km/years/"
files = sorted(os.listdir(path_d))
if ".DS_Store" in files: files.remove(".DS_Store")

ds_i = []

for f in files:
    ds_i.append( xr.open_dataset( path_d + f ).isel( {"lat": [i]} ) )

ds = xr.concat(ds_i, dim = "time").to_netcdf(
    f"temp/WRF_miroc_1985_2014_{n}km/grid/WRF_miroc_1985_2014_{n}km_{i}.nc" )