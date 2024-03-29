import os

import numpy as np
import pandas as pd

import xarray as xr

path_d = "temp/quantile_vars/"
path_r = "temp/CDF_vars_model/"

vars = [ "Pressure", "Relative_Humidity", "Temperature",
    "Wind_Direction", "Wind_Speed", "DNI", "GHI", "UVHI" ]

# Iteramos para todas las variables a mapear.
for v in vars:

    files = os.listdir(path_d + v + "/")
    if ".DS_Store" in files: files.remove(".DS_Store")
    f = files[0]

    with xr.open_dataset(path_d + v + "/" + f) as ds:
        df = ds.to_dataframe().drop( ["XLAT", "XLONG"], axis = 1 )

        # A las variables de radiación les quitamos los ceros.
        if v in vars[-3:]: df = df[ df>0 ].dropna()

        latitude = df.index.get_level_values("south_north").unique()
        longitude = df.index.get_level_values("west_east").unique()

        # Obtenemos la curva de distribución acumulada para cada celda.
        df["q_model"] = 0.0
        for lat in latitude:
            for lon in longitude:
                df_c = df.xs( (slice(None), lat, lon) ).sort_values(v)
                df_c["q_model"] = np.linspace(
                    1/df_c.shape[0], 1, df_c.shape[0] )
                df.loc[ (slice(None), lat, lon), "q_model"
                    ] = df_c["q_model"].values

        ds["q_model"] = df["q_model"].to_xarray()
        # Guardamos el archivo.
        ds.to_netcdf(path_r + v + "/" + f, mode = "w" )