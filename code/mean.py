# Obtiene los valores promedio de las variables.

import sys

import numpy as np
import pandas as pd

import xarray as xr

name = sys.argv[1]
y_i  = sys.argv[2]
y_f  = sys.argv[3]

GHI  = ( xr.load_dataset(f"temp/{name}_sum.nc").drop(
    "time_bnds" )["GHI"] / ( int(y_f) - int(y_i) + 1) )
PROM = xr.load_dataset(f"temp/{name}_mean.nc").drop(
    "time_bnds" )
PROM["GHI"] = GHI
PROM.to_netcdf(f"results/{name}_prom.nc")