# Convierte de CSV a NetCDF.

import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

# Datos de entrada
name = sys.argv[1]
lat = name[-12:-7]
lon = name[-6:]
#longitud = []
#fnames = os.listdir(name)
#if ".DS_Store" in fnames: fnames.remove(".DS_Store")
#for f in fnames: longitud.append(f[-6:])
years  = list( range( int(sys.argv[2]), int(sys.argv[3]) + 1) )
months = list( range(1, 13) )
columns = [ "Year", "Month", "Day", "Hour", "Minute",
    "Temperature", "Dew Point", "Wind Speed", "GHI" ]

# Unimos todos los años.
df = pd.DataFrame( columns = columns )
for file in os.listdir(name):
    df = df.append( pd.read_csv( f"{name}/{file}", skiprows = 2 ) )

# Convertimos a fecha.
df["Time"] = pd.to_datetime( df["Year"].astype(str) + "/"
    + df["Month"].astype(str) + "/" + df["Day"].astype(str)
    + " " + df["Hour"].astype(str) + ":00:00" )

# Corregimos formato de columnas.
df = df.drop( columns[0:5], axis = 1 )

# Convertimos a Dataset.
df["Latitud" ] = float(lat)
df["Longitud"] = float(lon)
df.set_index( ["Time", "Latitud", "Longitud"]).astype(float).round(
    decimals = 1 ).to_xarray().to_netcdf(f"{name[:-18]}NetCDF/{lat}_{lon}.nc")