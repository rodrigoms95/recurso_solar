# Convierte de CSV a NetCDF.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

# Datos de entrada
path_d = sys.argv[1]
path_r = sys.argv[2]
files = os.listdir(path_d)
if ".DS_Store" in files: files.remove(".DS_Store")

#cols = [ "time", "Temperature", "DNI", "GHI", "Wind Speed",
#    "Global Horizontal UV Irradiance (280-400nm)",
#    "Global Horizontal UV Irradiance (295-385nm)" ]
cols = [ "time", "Temperature", "DNI", "GHI", "Wind Speed", "Ozone" ]

for f in sorted(files):
    lat = f[:5]
    lon = f[6:-4]

    print(f" Procesando coordenadas {lat}°N {lon}°W...    ", end = "\r")

    if not os.path.exists(f"{path_r}/{lat[0:2]}/{lat}/"):
        os.mkdir(f"{path_r}/{lat[0:2]}/{lat}/")

    if not os.path.exists(f"{path_r}/{lat[0:2]}/{lat}/{lat}_{lon}.nc"):
        df = pd.read_csv( f"{path_d}/{f}", index_col = "time",
            usecols = cols, parse_dates = True ).reset_index()

        # Convertimos a Dataset.
        df["lat" ] = float(lat)
        df["lon"] = float(lon)
        ds = df.set_index( ["time", "lat", "lon"] ).astype( float
            ).round( decimals = 1 ).to_xarray()
        ds["lat"] = ds["lat"].assign_attrs( standard_name = "latitude",
                long_name = "Latitude", units = "degrees" )
        ds["lon"] = ds["lon"].assign_attrs( standard_name = "longitude",
                long_name = "Longitude", units = "degrees" )
        ds.to_netcdf( f"{path_r}/{lat[0:2]}/{lat}/{lat}_{lon}.nc" )