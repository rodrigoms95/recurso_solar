import xarray as xr
import numpy as np
import pandas as pd

dir_n = "/home/rodr/buffalo/rodr/Datos/NSRDB/"
dir_p = "/datos/rodr/temp/recurso_solar/duck_curve/"
file_p = f"{dir_p}conus_points.csv"
file_d = f"{dir_n}nsrdb_conus_irradiance_2022.h5"
file_r = f"{dir_p}nsrdb_conus_irradiance_2022_ghi_time.nc"
ds = xr.open_dataset(file_d,
    drop_variables = ["dni", "fill_flag", "time_index", "dhi"],
    chunks = "auto").rename_dims(
    {"phony_dim_1": "points"}).isel(
    {"phony_dim_0": slice(0, None, 12)}
    ).astype(np.int16
    ).to_netcdf(file_r, compute = True)