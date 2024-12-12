# Obtenemos malla de puntos
import os
import xarray as xr
import pandas as pd
import numpy as np
from dask.diagnostics import ProgressBar

# Cargamos datos
dir_p = "/home/rodr/temp/recurso_solar/net_load/"
dir_d = "/datos/rodr/recurso_solar/net_load/"
file_p = f"{dir_p}nsrdb_points.csv"
points = pd.read_csv(file_p, index_col = 0).sort_index().index

files = os.listdir(dir_d)
for f in files:
    print(f)
    ds = xr.open_dataset(dir_d + files[0])
    ds = ds.isel({"time": slice(None, None, 2), "points": points})
    ds.to_netcdf(f"{dir_d}{f}_points.nc")
