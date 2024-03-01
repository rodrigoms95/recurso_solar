# Une todos los años en un solo CSV.

import os
import sys

import numpy as np
import pandas as pd

# Datos.
name = sys.argv[1]
y_i = sys.argv[2]
y_f = sys.argv[3]
years  = list( range( int(y_i), int(y_f) + 1) )
months = list( range(1, 13) )
columns = [ "Year", "Month", "Day", "Hour", "Minute", "Temperature", "GHI",
    "DNI", "Relative Humidity", "Pressure", "Wind Speed", "Wind Direction" ]

# Rutas de archivos
path_d = f"data/{name}/"
path_r = f"temp/{name}/"
if not os.path.exists(path_r): os.mkdir(path_r)
dirs = os.listdir(path_d)
if ".DS_Store" in dirs: dirs.remove(".DS_Store")

# Unimos los CSV.

for d in dirs:
    lat = d[0:5]
    lon = d[-6:]

    # Unimos todos los años.
    df = pd.DataFrame( columns = columns )
    files = os.listdir(f"{path_d}{d}")
    if ".DS_Store" in files: files.remove(".DS_Store")
    for f in files:
        df = df.append( pd.read_csv( f"{path_d}{d}/{f}", skiprows = 2 ) )

    # Convertimos a fecha.
    df["time"] = pd.to_datetime( df["Year"].astype(str) + "/"
        + df["Month"].astype(str) + "/" + df["Day"].astype(str)
        + " " + df["Hour"].astype(str) + ":00:00" )
    
    # Corregimos formato de columnas.
    df = df.drop( columns[0:5], axis = 1 ).set_index(
        "time" ).sort_index().round( decimals = 2 )
    
    # Guardamos el archivo.
    df.to_csv(f"{path_r}{lat}_{lon}.csv")