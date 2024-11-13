import xarray as xr
import pandas as pd

dir_p = "/datos/rodr/temp/recurso_solar/duck_curve/"

ds = xr.open_mfdataset(f"{dir_p}/points/*.nc")
ds["time"] = pd.date_range("2022-01-01", "2023-01-01", freq = "1h")[:-1]
ds.to_netcdf(f"{dir_p}full_disc_pv_2022.nc")