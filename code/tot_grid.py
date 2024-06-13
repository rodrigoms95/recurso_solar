import os
import sys

import xarray as xr

import xesmf as xe


i = int(sys.argv[1])
internal = sys.argv[2]
name = sys.argv[3]
path_d = f"{internal}/"

xr.open_dataset( f"{internal}/{name}.nc" ).isel( {"lat": [i]} ).to_netcdf(
    f"{internal}/grid/{name}_{i}.nc" )