# Obtenemos malla de puntos
import os
import xarray as xr
import pandas as pd
import numpy as np
from dask.diagnostics import ProgressBar

# Cargamos datos
dir_d = "/home/rodr/buffalo/rodr/temp/"
dir_r = "/datos/rodr/recurso_solar/net_load/"
file_p = f"{dir_r}nsrdb_points.csv"
#points = pd.read_csv(file_p, index_col = 0).sort_index().index

files = os.listdir(dir_d)
vars = ["ghi", "dni", "relative_humidity", "air_temperature", "wind_speed"]
ds = xr.open_dataset(dir_d + files[0], chunks = {"phony_dim_1": 100000})
ds = ds.rename_vars({"time_index": "time"}).set_coords("time").swap_dims(
    {"phony_dim_0": "time"}).rename_dims({"phony_dim_1": "points"})[vars]
ds["time"] = ds["time"].astype(np.datetime64)
ds = ds.astype(np.int16)
#ds = ds.isel({"time": slice(None, None, 2),
#    "points": points})
ds.to_netcdf(f"{dir_r}{files[0].split('.')[0]}.nc")