# Convierte de CSV a NetCDF.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

# Datos de entrada
path_d = sys.argv[1]
path_r = sys.argv[2]
name = sys.argv[3]
files = os.listdir(path_d)

if name == "NSRDB_4km":
    cols = [ "time", "Temperature", "GHI", "DNI", "Wind Speed", "Pressure",
        "Global Horizontal UV Irradiance (280-400nm)",
        "Global Horizontal UV Irradiance (295-385nm)" ]
elif name == "NSRDB_2km":
    cols = [ "time", "Temperature", "DNI", "GHI", "Wind Speed", "Pressure" ]

for f in sorted(files):
    lat = f[:5]
    lon = f[6:-4]

    print(f"Procesando coordenadas {lat}°N {lon}°W...")
    if f[0:1] == ".": os.remove(f"{path_d}/{f}")
    else:
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
            ds["Pressure"] = ds["Pressure"] * 100
            if name == "NSRDB_4km":
                ds["UVHI"] = (
                    ds["Global Horizontal UV Irradiance (280-400nm)"] +
                    ds["Global Horizontal UV Irradiance (295-385nm)"]
                    ).astype(np.float32)
                ds = ds.drop_vars(
                    ["Global Horizontal UV Irradiance (280-400nm)",
                    "Global Horizontal UV Irradiance (295-385nm)"] )
            ds = ds.rename_vars( {"Wind Speed": "Wind_Speed"} )
            ds.to_netcdf( f"{path_r}/{lat[0:2]}/{lat}/{lat}_{lon}.nc" )