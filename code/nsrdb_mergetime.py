# Une todos los años en un solo CSV.

import os
import sys

import numpy as np
import pandas as pd

    # Datos.

# Rutas de archivos
path_d = sys.argv[1]
path_r = sys.argv[2]
name = sys.argv[3]
if not os.path.exists(path_r): os.mkdir(path_r)
dirs = sorted(os.listdir(path_d))

if name == "NSRDB_4km":
    columns = [ "Year", "Month", "Day", "Hour", "Minute", "Temperature",
        "Dew Point", "DNI", "DHI", "GHI", "Relative Humidity",
        "Solar Zenith Angle", "Precipitable Water", "Pressure",
        "Surface Albedo", "Wind Direction", "Wind Speed",
        "Global Horizontal UV Irradiance (280-400nm)",
        "Global Horizontal UV Irradiance (295-385nm)" ]
elif name == "NSRDB_2km":
    columns = [ "Year", "Month", "Day", "Hour", "Minute", "DHI",
        "Temperature", "Dew Point", "DNI", "GHI", "Ozone",
        "Relative Humidity", "Solar Zenith Angle", "Surface Albedo",
        "Pressure", "Precipitable Water", "Wind Direction", "Wind Speed"]

# Unimos los CSV.
for d in dirs:
    if d[0] != ".":
        lat = d[0:5]
        lon = d[6:]
        print(f"Procesando coordenadas {lat}°N {lon}°W...")
        
        if not os.path.exists(f"{path_r}/{lat}_{lon}.csv"):
            # Unimos todos los años.
            df = pd.DataFrame( [ [0.0] * len(columns) ], columns = columns )
            files = sorted( os.listdir(f"{path_d}/{d}") )
            for f in files:
                if f[0] == ".": os.remove(f"{path_d}/{d}/{f}")
                else:
                    df = pd.concat( [ df, pd.read_csv( f"{path_d}/{d}/{f}",
                        header = 0, usecols = columns ) ] )
            df = df.iloc[1:]
        
            # Convertimos a fecha.
            df["time"] = pd.to_datetime( df["Year"].astype(int).astype(str)
                + "/" + df["Month"].astype(int).astype(str) + "/"
                + df["Day"].astype(int).astype(str) + " "
                + df["Hour"].astype(int).astype(str) + ":00:00" )
            
            # Corregimos formato de columnas.
            df = df.drop( columns[0:5], axis = 1 ).set_index(
                "time" ).sort_index().round( decimals = 4 )
            
            # Guardamos el archivo.
            df.to_csv(f"{path_r}/{lat}_{lon}.csv")
    
print()