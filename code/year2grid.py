import os
import sys

import xarray as xr

import xesmf as xe


i = int(sys.argv[1])
internal = sys.argv[2]
name= sys.argv[3]
path_d = f"{internal}/years/"
files = sorted(os.listdir(path_d))
if ".DS_Store" in files: files.remove(".DS_Store")

ds_i = []

for f in files:
    ds_i.append( xr.open_dataset( path_d + f ).isel( {"lat": [i]} ) )

ds = xr.concat( ds_i, dim = "time" 
    ).to_netcdf( f"{internal}/grid/{name}_{i}.nc" )