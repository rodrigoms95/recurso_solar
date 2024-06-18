import os
import sys

import xarray as xr

import xesmf as xe


i = int(sys.argv[1])
internal = sys.argv[2]
path_data = sys.argv[3]
name = sys.argv[4]

xr.open_dataset( f"{path_data}/{name}.nc"
    ).isel( {"lat": slice(9, -9), "lon": slice(8,  -10)}
    ).isel( {"lat": [i]} ).to_netcdf( f"{internal}/grid/{name}_{i}.nc" )