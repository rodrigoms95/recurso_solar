import os
import sys

import numpy as np
import pandas as pd

import xarray as xr

n = sys.argv[1]
lat = int(sys.argv[2])
internal = sys.argv[3]

path_d = f"{internal}/WRF_miroc_1985_2014/NSRDB_{n}km.nc"
path_r = f"{internal}/NSRDB_{n}km/vars/"

if n == 2: vars = [ "Pressure", "Temperature", "Wind Speed", "DNI", "GHI" ]
else     : vars = [ "UVHI" ]

with xr.open_dataset(path_d) as ds:

    for v in vars:
        print(f"Variable {v}...")

        for i in range(lat):
            print(f"Procesando latitud {i+1}/{lat}", sep = "\r")

            if not os.path.exists(
                f"{path_r}{v}/WRF_miroc_1985_2014_{n}km_{i}.nc" ):
        
                df = ds[[v]].isel({"lat": [i]}).to_dataframe()

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

                ds["q_model"] = df["q_model"].to_xarray()
                # Guardamos el archivo.
                ds.to_netcdf( f"{path_r}{v}/NSRDB_{n}km_{v}_{i}.nc",
                    mode = "w" )