import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
from dask.diagnostics import ProgressBar

# Cargamos datos.
scn   = sys.argv[1]
file  = sys.argv[2]
dir_o = "/datos/rodr/Datos/WRF/"
dir_d = f"{dir_o}{scn}/"

vrad  = ["GHI", "P_mp"]

with xr.open_dataset(f"{dir_d}{scn}{file}.nc",
    chunks = {"south_north": 10, "west_east": 10}) as ds:

    vars = ds.keys()
    ds_res = ds.drop_vars(vars)
    for v in vars:

        if not os.path.exists(f"{dir_d}{scn}{file}_cdf.nc"):
        
            df = ds[[v]].to_dataframe().drop(columns = ["XLAT", "XLONG"])

            # A las variables de radiación les quitamos los ceros.
            if v in vrad: df = df[ df>0 ].dropna()

            latitude = df.index.get_level_values("south_north").unique()
            longitude = df.index.get_level_values("west_east").unique()

            # Obtenemos la curva de distribución acumulada para cada celda.
            df["cdf"] = 0.0
            for lat in latitude:
                for lon in longitude:
                    df_c = df.xs( (slice(None), lat, lon) ).sort_values(v)
                    df_c["cdf"] = np.linspace(
                        1/df_c.shape[0], 1, df_c.shape[0] )
                    df.loc[ (slice(None), lat, lon), "cdf"
                        ] = df_c["cdf"].values

            ds_res[v + "_cdf"] = df["cdf"].to_xarray()
    
    # Guardamos el archivo.
    delayed = ds_res.to_netcdf(f"{dir_d}{scn}{file}_cdf.nc", compute = False)
    with ProgressBar(): 
        print(f"Calculando {dir_d}{scn}{file}_cdf.nc")
        delayed.compute()