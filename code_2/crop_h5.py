import xarray as xr
import h5py
import pandas as pd
import numpy as np

dir_d  = "/home/rodr/buffalo/rodr/Datos/NSRDB/"
file_d = "nsrdb_full_disc_pv_2022.h5"
dir_r  = "/datos/rodr/Datos/NSRDB/"
file_r = "nsrdb_full_disc_wind_temp_2022.nc"

with h5py.File(dir_d + file_d) as f:
    temp_psm = f['wind_speed'].attrs['psm_scale_factor']
    wind_psm = f['wind_speed'].attrs['psm_scale_factor']
    print(f"Air temperature scale factor: {temp_psm}")
    print(f"Wind speed scale factor: {wind_psm}")
    meta = pd.DataFrame(f['meta'][...])
points = meta[ (meta["country"]==b"Mexico")
    | (meta["state"].isin([b"Texas", b"California", b"Nevada"])) ]
ds = xr.open_dataset(dir_d + file_d)
ds_2 = ds.isel(phony_dim_1 = points.index.values, phony_dim_0 =
    slice(0, None, 3)).drop_vars("wind_direction").rename_vars(
    {"time_index": "time"}).set_coords("time").swap_dims(
    {"phony_dim_0": "time"}).rename_dims({"phony_dim_1": "points"})
ds_2["latitude"] = (("points"), points["latitude"].values)
ds_2["longitude"] = (("points"), points["longitude"].values)
#ds_2["air_temperature"] = ds_2["air_temperature"].astype(np.int16)
#ds_2["wind_speed"] = ds_2["wind_speed"].astype(np.int16)
#ds_2["time"] = pd.to_datetime(ds_2["time"])
print(f"Original size: {ds.nbytes/1024**3:,.0f} GB")
print(f"Cropped size: {ds_2.nbytes/1024**3:,.0f} GB")
ds_2.to_netcdf(dir_r + file_r)