# Une todos los años en un solo CSV.

import os
import sys

import numpy as np
import pandas as pd

# Datos.
columns = [ "Year", "Month", "Day", "Hour", "Minute", "Temperature",
    "Dew Point", "DNI", "DHI", "GHI", "Relative Humidity",
    "Solar Zenith Angle", "Precipitable Water", "Pressure", "Surface Albedo",
    "Wind Direction", "Wind Speed",
    "Global Horizontal UV Irradiance (280-400nm)",
    "Global Horizontal UV Irradiance (295-385nm)" ]
#columns = [ "Year", "Month", "Day", "Hour", "Minute", "DHI", "Temperature",
#    "Dew Point", "DNI", "GHI", "Ozone", "Relative Humidity",
#    "Solar Zenith Angle", "Surface Albedo", "Pressure", "Precipitable Water",
#    "Wind Direction", "Wind Speed"]

# Rutas de archivos
path_d = sys.argv[1]
path_r = sys.argv[2]
if not os.path.exists(path_r): os.mkdir(path_r)
dirs = os.listdir(path_d)
if ".DS_Store" in dirs: dirs.remove(".DS_Store")

# Unimos los CSV.

for d in dirs:
    lat = d[0:5]
    lon = d[6:]
    print(f" Procesando coordenadas {lat}°N {lon}°W...    ", end = "\r")
    
    if not os.path.exists(f"{path_r}{lat}_{lon}.csv"):
        # Unimos todos los años.
        df = pd.DataFrame( [ [0.0] * len(columns) ], columns = columns )
        files = os.listdir(f"{path_d}{d}")
        if ".DS_Store" in files: files.remove(".DS_Store")
        for f in files:
            df = pd.concat( [ df, pd.read_csv( f"{path_d}{d}/{f}",
                header = 0, names = columns ) ] )
        df = df.iloc[1:]
    
        # Convertimos a fecha.
        df["time"] = pd.to_datetime( df["Year"].astype(int).astype(str) + "/"
            + df["Month"].astype(int).astype(str) + "/"
            + df["Day"].astype(int).astype(str) + " "
            + df["Hour"].astype(int).astype(str) + ":00:00" )
        
        # Corregimos formato de columnas.
        df = df.drop( columns[0:5], axis = 1 ).set_index(
            "time" ).sort_index().round( decimals = 4 )
        
        # Guardamos el archivo.
        df.to_csv(f"{path_r}{lat}_{lon}.csv")