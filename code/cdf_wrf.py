import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

i = sys.argv[1]
n = sys.argv[2]
internal = sys.argv[3]
dataset = sys.argv[4]
directory = sys.argv[5]

path_d = f"{internal}/{dataset}_{n}km/{directory}/"
path_r = f"{internal}/{dataset}_{n}km/vars/"

vars = [ "Pressure", "Temperature", "Wind Speed", "DNI", "GHI", "UVHI" ]

with xr.open_dataset(f"{path_d}{dataset}_{n}km_{i}.nc") as ds:

    for v in vars:

        if not os.path.exists(f"{path_r}{v}/{dataset}_{n}km_{i}.nc"):
        
            ds_v = ds[[v]]
            df = ds[[v]].to_dataframe()

            # A las variables de radiación les quitamos los ceros.
            if v in vars[-2:]: df = df[ df>0 ].dropna()

            latitude = df.index.get_level_values("lat").unique()
            longitude = df.index.get_level_values("lon").unique()

            # Obtenemos la curva de distribución acumulada para cada celda.
            df["q_model"] = 0.0
            for lat in latitude:
                for lon in longitude:
                    df_c = df.xs( (slice(None), lat, lon) ).sort_values(v)
                    df_c["q_model"] = np.linspace(
                        1/df_c.shape[0], 1, df_c.shape[0] )
                    df.loc[ (slice(None), lat, lon), "q_model"
                        ] = df_c["q_model"].values

            ds_v["q_model"] = df["q_model"].to_xarray()
            # Guardamos el archivo.
            ds_v.to_netcdf( f"{path_r}{v}/{dataset}_{n}km_{i}.nc", mode = "w" )