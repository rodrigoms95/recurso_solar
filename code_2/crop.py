import xarray as xr
import pandas as pd
import numpy as np
from dask.diagnostics import ProgressBar

dir_d = "/datos/rodr/temp/recurso_solar/duck_curve_1/"
dir_r = "/datos/rodr/temp/recurso_solar/duck_curve/"
names = ["full_disc_irradiance_2022.nc", "full_disc_climate_2022.nc"]
points = pd.read_csv(f"{dir_d}conus_points.csv", index_col = 0).index
#ds_1 = xr.open_dataset(f"{dir_d}{names[0]}",
#    ).sortby("points").chunk({"points": 20000}).sel({"points": points})
ds_2 = xr.open_dataset(f"{dir_d}{names[1]}",
    ).sortby("points").chunk({"points": 20000}).sel({"points": points})
#delayed_obj_1 = ds_1.to_netcdf(f"{dir_r}{names[0]}", compute = False)
delayed_obj_2 = ds_2.to_netcdf(f"{dir_r}{names[1]}", compute = False)
with ProgressBar():
    #print(names[0])
    #results_1 = delayed_obj_1.compute()
    print(names[1])
    results_2 = delayed_obj_2.compute()
