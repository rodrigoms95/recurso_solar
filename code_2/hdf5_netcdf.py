import xarray as xr
import numpy as np
import pandas as pd
import os

print("Slicing dataset")
print()

dir_n = "/home/rodr/buffalo/rodr/Datos/NSRDB/"
dir_p = "/datos/rodr/temp/recurso_solar/duck_curve/"
file_p = f"{dir_p}conus_points.csv"
file_d = f"{dir_n}nsrdb_conus_pv_2022.h5"
file_r = f"{dir_p}nsrdb_conus_pv_2022_crop.nc"
points = pd.read_csv(file_p, index_col = 0).sort_index().index
ds = xr.open_dataset(file_d,
    drop_variables = ["dni", "fill_flag", "time_index"], chunks = "auto"
    ).rename_dims({"phony_dim_1": "points", "phony_dim_0": "time"})

if not os.path.exists(f"{dir_p}points/"): os.mkdir(f"{dir_p}points/")

for j in range(0, np.ceil(points.shape[0]/1000).astype(int)):
    if not os.path.exists(f"{dir_p}points/points_{j}.nc"):
        print(j*1000)

        df = ds.isel(time = slice(0, None, 12), points = points[0 + 1000*j]
            ).to_dataframe().astype(np.int16)

        for i in range(1 + 1000*j,1000 + 1000*j):
            if i<points.shape[0]:
                p = points[i]
                df = pd.concat([df, ds.isel(time = slice(0, None, 12),
                    points = p).to_dataframe().astype(np.int16)])
        
        df["points"] = np.repeat(points[0+j*1000:1000+j*1000],
            ds["time"].shape[0]/12)
        df.reset_index().set_index(["points", "time"]).to_xarray().to_netcdf(
            f"{dir_p}points/points_{j}.nc")
