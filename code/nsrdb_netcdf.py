# Convierte de CSV a NetCDF.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

# Datos de entrada
name = sys.argv[1]
lat = name[-16:-11]
lon = name[-10:-4]
years  = list( range( int(sys.argv[2]), int(sys.argv[3]) + 1) )
months = list( range(1, 13) )

df = pd.read_csv( name, index_col = "time", parse_dates = True,
    infer_datetime_format = True ).reset_index()

# Convertimos a Dataset.
df["lat" ] = float(lat)
df["lon"] = float(lon)
ds = df.set_index( ["time", "lat", "lon"]).astype(float).round(
    decimals = 1 ).to_xarray()
ds["lat"] = ds["lat"].assign_attrs( standard_name = "latitude",
        long_name = "Latitude", units = "degrees" )
ds["lon"] = ds["lon"].assign_attrs( standard_name = "longitude",
        long_name = "Longitude", units = "degrees" )
ds.to_netcdf( f"temp/NetCDF/{lat}_{lon}.nc" )