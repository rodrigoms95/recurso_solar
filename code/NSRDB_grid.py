import os
import sys

import xarray as xr

import xesmf as xe


i = int(sys.argv[1])
n = int(sys.argv[2])
internal = sys.argv[3]

path_d = f"{internal}/WRF_miroc_1985_2014/NSRDB_{n}km.nc"

ds = xr.open_dataset( path_d ).isel( {"lat": [i]} ).to_netcdf(
    f"{internal}/NSRDB_{n}km/grid/NSRDB_{n}km_{i}.nc" )